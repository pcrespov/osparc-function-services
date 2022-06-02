#!/bin/sh
set -o errexit
set -o nounset
IFS=$(printf '\n\t')

INFO="INFO: [$(basename "$0")] "
WARNING="WARNING: [$(basename "$0")] "
ERROR="ERROR: [$(basename "$0")] "

# This entrypoint script:
#
# - Executes *inside* of the container upon start as --user [default root]
# - Notice that the container *starts* as --user [default root] but
#   *runs* as non-root user [$SC_USER_NAME]
#
echo "$INFO" " Entrypoint for stage '${SC_BUILD_TARGET}' ..."
echo "$INFO" " User    : $(id "$(whoami)")"
echo "$INFO" " Workdir : $(pwd)"

# expect input/output folders to be mounted
stat "${INPUT_FOLDER}" >/dev/null 2>&1 ||
    (echo "$ERROR" " You must mount '${INPUT_FOLDER}' to deduce user and group ids" && exit 1)
stat "${OUTPUT_FOLDER}" >/dev/null 2>&1 ||
    (echo "$ERROR" " You must mount '${OUTPUT_FOLDER}' to deduce user and group ids" && exit 1)

# NOTE: expects docker run ... -v /path/to/input/folder:${INPUT_FOLDER}
# check input/output folders are owned by the same user
if [ "$(stat -c %u "${INPUT_FOLDER}")" -ne "$(stat -c %u "${OUTPUT_FOLDER}")" ]; then
    echo "$ERROR" " '${INPUT_FOLDER}' and '${OUTPUT_FOLDER}' have different user id's. not allowed" && exit 1
fi
# check input/outputfolders are owned by the same group
if [ "$(stat -c %g "${INPUT_FOLDER}")" -ne "$(stat -c %g "${OUTPUT_FOLDER}")" ]; then
    echo "$ERROR" " '${INPUT_FOLDER}' and '${OUTPUT_FOLDER}' have different group id's. not allowed" && exit 1
fi

echo "$INFO" " setting correct user id/group id..."

HOST_USERID=$(stat --format=%u "${INPUT_FOLDER}")
HOST_GROUPID=$(stat --format=%g "${INPUT_FOLDER}")
CONTAINER_GROUP=$(getent group "${HOST_GROUPID}" | cut --delimiter=: --fields=1)

if [ "$HOST_USERID" -eq 0 ]; then
    echo "$WARNING" " Folder mounted owned by root user... adding $SC_USER_NAME to root..."
    adduser "$SC_USER_NAME" root
else
    echo "$INFO" " Folder mounted owned by user $HOST_USERID:$HOST_GROUPID-'$CONTAINER_GROUP'..."
    # take host's credentials in $SC_USER_NAME
    if [ -z "$CONTAINER_GROUP" ]; then
        echo "$INFO" " Creating new group my$SC_USER_NAME"
        CONTAINER_GROUP=my$SC_USER_NAME
        addgroup --gid "$HOST_GROUPID" "$CONTAINER_GROUP"
    else
        echo "$INFO" " group already exists"
    fi
    echo "$INFO" " adding $SC_USER_NAME to group $CONTAINER_GROUP..."
    adduser "$SC_USER_NAME" "$CONTAINER_GROUP"

    echo "$INFO" " changing $SC_USER_NAME:$SC_USER_NAME ($SC_USER_ID:$SC_USER_ID) to $SC_USER_NAME:$CONTAINER_GROUP ($HOST_USERID:$HOST_GROUPID)"
    usermod --uid "$HOST_USERID" --gid "$HOST_GROUPID" "$SC_USER_NAME"

    echo "$INFO" " Changing group properties of files around from $SC_USER_ID to group $CONTAINER_GROUP"
    find / -path /proc -prune -o -path /sys -prune -o -group "$SC_USER_ID" -exec chgrp --no-dereference "$CONTAINER_GROUP" {} \;
    # change user property of files already around
    echo "$INFO" " Changing ownership properties of files around from $SC_USER_ID to group $CONTAINER_GROUP"
    find / -path /proc -prune -o -path /sys -prune -o -user "$SC_USER_ID" -exec chown --no-dereference "$SC_USER_NAME" {} \;
fi

echo "$INFO" " Starting $* ..."
echo "$INFO" " $SC_USER_NAME rights    : $(id "$SC_USER_NAME")"
echo "$INFO" " local dir : $(ls -al)"
echo "$INFO" " input dir : $(ls -al "${INPUT_FOLDER}")"
echo "$INFO" " output dir : $(ls -al "${OUTPUT_FOLDER}")"
echo "$INFO" " HOST_USERID=${HOST_USERID}"
echo "$INFO" " HOST_GROUPID=${HOST_GROUPID}"
echo "$INFO" " CONTAINER_GROUP=${CONTAINER_GROUP}"

exec gosu "$SC_USER_NAME" "$@"
