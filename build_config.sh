#!/bin/sh
sh gen_base_config.sh && npr validate auto_config.cfg && cp auto_config.cfg config.cfg
