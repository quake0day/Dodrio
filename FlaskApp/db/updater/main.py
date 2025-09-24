from flask import Flask, render_template, request, redirect, url_for
import ldap

app = Flask(__name__)

LDAP_SERVER = "ldap://your_ldap_server"
LDAP_USER = "your_ldap_user"
LDAP_PASSWORD = "your_ldap_password"
LDAP_BASE_DN = "ou=users,dc=example,dc=com"

def ldap_connect():
    conn = ldap.initialize(LDAP_SERVER)
    conn.simple_bind_s(LDAP_USER, LDAP_PASSWORD)
    return conn

def get_users(conn):
    search_filter = "(objectClass=inetOrgPerson)"
    attrs = ["uid", "userPassword"]
    result = conn.search_s(LDAP_BASE_DN, ldap.SCOPE_SUBTREE, search_filter, attrs)
    users = [(entry[1]["uid"][0].decode(), entry[1]["userPassword"][0].decode()) for entry in result]
    return users

def change_password(conn, uid, new_password):
    dn = f"uid={uid},{LDAP_BASE_DN}"
    new_values = {'userPassword': [new_password.encode()]}
    ldif = ldap.modlist.modifyModlist({}, new_values)
    conn.modify_s(dn, ldif)

@app.route('/')
def index():
    conn = ldap_connect()
    users = get_users(conn)
    conn.unbind_s()
    return render_template('index.html', users=users)

@app.route('/change_password', methods=['POST'])
def change_user_password():
    uid = request.form['uid']
    new_password = request.form['new_password']
    conn = ldap_connect()
    change_password(conn, uid, new_password)
    conn.unbind_s()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

# 1. Try generating with command K. Ask for a pytorch script of a feedforward neural network
# 2. Then, select the outputted code and hit chat. Ask if there's a bug. Ask how to improve.
# 3. Try selecting some code and hitting edit. Ask the bot to add residual layers.