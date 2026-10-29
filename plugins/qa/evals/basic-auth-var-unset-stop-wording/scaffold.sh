#!/usr/bin/env bash
#
# Stage the stub project of the micro case whose wording this case grades.

exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/../basic-auth-var-unset-stop/scaffold.sh"
