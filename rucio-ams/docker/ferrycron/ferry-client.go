package main

import (
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"net"
	"net/http"
	"net/url"
	"regexp"
	"time"

	opentracing "github.com/opentracing/opentracing-go"
	log "github.com/sirupsen/logrus"
)

//func spanLogger(l *log.Entry, span opentracing.Span) *log.Entry {
//        return l.WithField("traceid", span.Context().(jaeger.SpanContext).TraceID().String())
//}
//func logSpanError(l *log.Entry, span opentracing.Span, format string, args ...any) error {
//        err := fmt.Errorf(format, args...)
//        ext.LogError(span, err)
//        l.Error(err)
//        return err
//}

// Basic FERYY v2 response object.
// You probably want to replace FerryOutput with a concrete type.
type baseResp struct {
	FerryStatus string      `json:"ferry_status"`
	FerryError  []string    `json:"ferry_error"`
	FerryOutput interface{} `json:"ferry_output"`
}

// Ferry is a FERRY API client
type Ferry struct {
	URL    string
	Cert   string
	Key    string
	client *http.Client
}

// NewFerryClient inializes a FERRY API client.
func NewFerryClient(url, cert, key string) *Ferry {
	c := &Ferry{
		URL:    url,
		Cert:   cert,
		Key:    key,
		client: &http.Client{},
	}
	if cert != "" && key != "" {
		c.client.Transport = &http.Transport{
			Proxy: http.ProxyFromEnvironment,
			DialContext: (&net.Dialer{
				Timeout:   30 * time.Second,
				KeepAlive: 30 * time.Second,
				DualStack: true,
			}).DialContext,
			MaxIdleConns:          100,
			IdleConnTimeout:       90 * time.Second,
			TLSHandshakeTimeout:   10 * time.Second,
			ExpectContinueTimeout: 1 * time.Second,
			TLSClientConfig: &tls.Config{
				GetClientCertificate: func(*tls.CertificateRequestInfo) (*tls.Certificate, error) {
					cert, err := tls.LoadX509KeyPair(cert, key)
					return &cert, err
				},
				InsecureSkipVerify: true,
			},
		}

	}
	return c
}

// DoesUserHaveRoleForGroup checks if user has the given role in the given group.
// It assumes that roles are defined in FQANs like "/Role=Production"
func (c *Ferry) DoesUserHaveRoleForGroup(ctx context.Context, user, group string, role UserRole) bool {
	span, ctx := opentracing.StartSpanFromContext(ctx, "ferry.DoesUserHaveRoleForGroup")
	defer span.Finish()
	span.SetTag("user", user)
	span.SetTag("group", group)
	span.SetTag("role", role.String())
	l := spanLogger(log.WithFields(log.Fields{
		"user":  user,
		"group": group,
		"role":  role.String(),
	}), span)

	var resp struct {
		baseResp
		FerryOutput []struct {
			Group string `json:"unitname"`
			FQAN  string `json:"fqan"`
		} `json:"ferry_output"`
	}
	params := make(url.Values)
	params.Set("username", user)
	params.Set("unitname", group)
	if err := c.get(ctx, "getUserFQANs", params, &resp); err != nil {
		logSpanError(l, span, err.Error())
		return false
	}
	if len(resp.FerryError) > 0 {
		logSpanError(l, span, "FERRY returned errors: %s", resp.FerryError)
		return false
	}
	re, err := regexp.Compile(fmt.Sprintf("/Role=%s/", role))
	if err != nil {
		logSpanError(l, span, err.Error())
		return false
	}
	for _, r := range resp.FerryOutput {
		if re.MatchString(r.FQAN) {
			return true
		}
	}
	return false
}

// IsUserMemberOfGroup checks if user is a member of the given group.
func (c *Ferry) IsUserMemberOfGroup(ctx context.Context, user, group string) bool {
	span, ctx := opentracing.StartSpanFromContext(ctx, "ferry.IsUserMemberOfGroup")
	defer span.Finish()
	span.SetTag("user", user)
	span.SetTag("group", group)
	l := spanLogger(log.WithFields(log.Fields{
		"user":  user,
		"group": group,
	}), span)

	var resp struct {
		baseResp
		FerryOutput []struct {
			UnitName        string `json:"unitname"`
			AlternativeName string `json:"alternativename"`
		} `json:"ferry_output"`
	}
	params := make(url.Values)
	params.Set("username", user)
	if err := c.get(ctx, "getMemberAffiliations", params, &resp); err != nil {
		logSpanError(l, span, err.Error())
		return false
	}
	if len(resp.FerryError) > 0 {
		logSpanError(l, span, "FERRY returned errors: %s", resp.FerryError)
		return false
	}
	for _, u := range resp.FerryOutput {
		if u.UnitName == group {
			return true
		}
	}
	return false
}

// IsUserGroupSuperuser checks if user is a superuser for the given group.
func (c *Ferry) IsUserGroupSuperuser(ctx context.Context, user, group string) bool {
	span, ctx := opentracing.StartSpanFromContext(ctx, "ferry.IsUserGroupSuperuser")
	defer span.Finish()
	span.SetTag("user", user)
	span.SetTag("group", group)
	l := spanLogger(log.WithFields(log.Fields{
		"user":  user,
		"group": group,
	}), span)

	var resp struct {
		baseResp
		FerryOutput []struct {
			Uname string `json:"username"`
		} `json:"ferry_output"`
	}
	params := make(url.Values)
	params.Set("groupname", group)
	params.Set("grouptype", "BatchSuperusers")
	if err := c.get(ctx, "getGroupMembers", params, &resp); err != nil {
		logSpanError(l, span, err.Error())
		return false
	}
	if len(resp.FerryError) > 0 {
		logSpanError(l, span, "FERRY returned errors: %s", resp.FerryError)
		return false
	}
	for _, u := range resp.FerryOutput {
		if u.Uname == user {
			return true
		}
	}
	return false
}

func (c *Ferry) get(ctx context.Context, endpoint string, params url.Values, results interface{}) error {
	span, ctx := opentracing.StartSpanFromContext(ctx, "ferry.get")
	defer span.Finish()

	url := c.URL + "/" + endpoint

	fields := log.Fields{"url": url}
	span.SetTag("http.url", url)
	span.SetTag("http.method", "GET")
	for p, vs := range params {
		fields[p] = vs[0]
		span.SetTag(p, vs[0])
	}
	l := spanLogger(log.WithFields(fields), span)

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return logSpanError(l, span, err.Error())
	}
	req.URL.RawQuery = params.Encode()

	resp, err := c.client.Do(req)
	if err != nil {
		return logSpanError(l, span, "error querying FERRY: %s", err)
	}
	defer resp.Body.Close()
	span.SetTag("http.status_code", resp.StatusCode)
	l = l.WithField("response", resp.Status)
	if resp.StatusCode != 200 {
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			return logSpanError(l, span, "request error %d, and error reading response body: %w", resp.StatusCode, err)
		}
		l.WithFields(log.Fields{
			"status":     resp.Status,
			"statusCode": resp.StatusCode,
			"body":       fmt.Sprintf("%s", body),
		}).Debugf("error response from FERRY")
		return logSpanError(l, span, "request error %d: %s", resp.StatusCode, resp.Status)
	}

	var rr io.Reader = resp.Body
	dec := json.NewDecoder(rr)
	err = dec.Decode(results)
	if err != nil {
		return logSpanError(l, span, "error unmarshaling FERRY response: %w", err)
	}
	return nil
}
