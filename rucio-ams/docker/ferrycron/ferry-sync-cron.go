package main

import (
	"context"

	log "github.com/sirupsen/logrus"
)

const FERRY_URL = "https://ferry.fnal.gov:8445"

var ADMIN_USERS = [...]string{"bjwhite", "dylee", "illingwo", "mengel"}

var exp_vip_accts = map[string]string{
	"dune":   "dunepro",
	"icarus": "icaruspro",
	"mu2e":   "mu2epro",
}

func run_program(ctx context.Context) int {
	// Get the program arguments settled
	var program_args = make(map[string]string)
	if args_rc, a := get_args(); args_rc != 0 {
		return args_rc
	} else {
		program_args = a
		log.WithFields(log.Fields{
			"experiment":  program_args["experiment"],
			"rucii":       program_args["rucii"],
			"FERRY URL":   FERRY_URL,
			"Admin users": ADMIN_USERS,
			"VIPs":        exp_vip_accts,
		}).Info("Program arguments: ")
	}

	// Get the users and DNs associated with the given Virtual Organization
	if ferryinfo_rc, ferry_vo_user_info := get_ferry_vo_user_info(ctx); ferryinfo_rc != 0 {
		return ferryinfo_rc
	} else {
		log.WithFields(log.Fields{
			"Info": ferry_vo_user_info,
		}).Info("Ferry VO Users: ")
	}

	// Add the users that need adding, disable the ones that need disabling
	if userprocessing_rc, num_vo_users_add, num_vo_users_del := process_vo_rucio_users(ctx); userprocessing_rc != 0 {
		return userprocessing_rc
	} else {
		log.WithFields(log.Fields{
			"Added":   num_vo_users_add,
			"Deleted": num_vo_users_del,
		}).Info("Users Processed: ")
	}

	// Add the identities that need adding, remove the ones that need removing
	if idprocessing_rc, num_vo_id_add, num_vo_id_del := process_vo_rucio_identities(ctx); idprocessing_rc != 0 {
		return idprocessing_rc
	} else {
		log.WithFields(log.Fields{
			"Added":   num_vo_id_add,
			"Deleted": num_vo_id_del,
		}).Info("Identities Processed: ")
	}

	return 0
}

func get_args() (int, map[string]string) {
	// Testing Arguments
	experiment := "hypot"
	rucii := "https://hypot-rucio.fnal.gov"

	prog_args := make(map[string]string)
	prog_args["experiment"] = experiment
	prog_args["rucii"] = rucii

	return 0, prog_args
}

func get_ferry_vo_user_info(ctx context.Context) (int, string) {
	var ferry_vo_user_info = "some big long list of user information"
	return 0, ferry_vo_user_info
}

func process_vo_rucio_users(ctx context.Context) (int, int, int) {
	var num_vo_users_add = 0
	var num_vo_users_del = 0
	if add_rc, num_add := add_vo_rucio_users(ctx); add_rc != 0 {
		num_vo_users_add = num_add
		return add_rc, num_vo_users_add, num_vo_users_del
	}
	if del_rc, num_del := del_vo_rucio_users(ctx); del_rc != 0 {
		num_vo_users_add = num_del
		return del_rc, num_vo_users_add, num_vo_users_del
	}
	return 0, num_vo_users_add, num_vo_users_del
}

func add_vo_rucio_users(ctx context.Context) (int, int) {
	return 0, 0
}

func del_vo_rucio_users(ctx context.Context) (int, int) {
	return 0, 0
}

func process_vo_rucio_identities(ctx context.Context) (int, int, int) {
	var num_vo_identites_add = 0
	var num_vo_identites_del = 0
	if add_rc, num_add := add_vo_rucio_identites(ctx); add_rc != 0 {
		num_vo_identites_add = num_add
		return add_rc, num_vo_identites_add, num_vo_identites_del
	}
	if del_rc, num_del := del_vo_rucio_identites(ctx); del_rc != 0 {
		num_vo_identites_add = num_del
		return del_rc, num_vo_identites_add, num_vo_identites_del
	}
	return 0, num_vo_identites_add, num_vo_identites_del
}

func add_vo_rucio_identites(ctx context.Context) (int, int) {
	return 0, 0
}

func del_vo_rucio_identites(ctx context.Context) (int, int) {
	return 0, 0
}

func main() {
	// Parse Arguments (experiment, muliple rucio, cert, key, capath)
	ctx := context.TODO()
	rc := run_program(ctx)
	log.WithFields(log.Fields{
		"Value": rc,
	}).Info("Final program return code: ")
	//
}
