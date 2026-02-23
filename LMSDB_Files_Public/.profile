# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
	. "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi

DAP_CONNECTION_STRING="postgresql://your_db_user:your_db_password@localhost/your_db_name"
DAP_API_URL="https://api-gateway.instructure.com/"
DAP_CLIENT_ID="your_dap_client_id"
DAP_CLIENT_SECRET="add_your_dap_client_secret"
PGPASSWORD="add_your_postgres_password"
API_KEYBETA="add_your_canvas_beta_api_key"
API_KEYLIVE="add_your_canvas_live_api_key" # sample placeholder for public repo
NGROK_AUTHTOKEN="add_your_ngrok_auth_token" 

DB_NAME="your_db_name"
DB_USER="your_db_user"
DB_PASSWORD="add_your_db_password"
DB_HOST="localhost"

export API_KEYBETA
export API_KEYLIVE
export PGPASSWORD
export DAP_CONNECTION_STRING
export DAP_API_URL
export DAP_CLIENT_ID
export DAP_CLIENT_SECRET
export NGROK_AUTHTOKEN
export DB_NAME
export DB_USER
export DB_PASSWORD
export DB_HOST

export PATH="$HOME/bin:$PATH"
