#!/bin/bash

app=$YNH_APP_INSTANCE_NAME

ensure_webkey_path_free() {
	if is_url_handled --domain="$domain" --path="/.well-known/openpgpkey"; then
		ynh_die "Another app already handles /.well-known/openpgpkey on $domain"
	fi
}
