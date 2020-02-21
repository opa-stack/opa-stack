/*
    Using root/admin roles for now, since there is not going to be anything sensitive
    in this database, and we need some time experimenting what works and not..

    Check out https://docs.mongodb.com/manual/core/security-built-in-roles/ for the builtin roles
*/

let res = [
    db.createUser({
        user: 'mongo',
        pwd: 'mongo',
        roles: [{
            role: 'root',
            db: 'admin',
        }, ],
    })
]

printjson(res)