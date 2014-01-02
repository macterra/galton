def SessionLogin(profile):
    print "SessionLogin", profile
    session.loggedin = True
    session.identifier = profile['identifier']
    session.name = profile.get('displayName')
    session.email = profile.get('email')
    session.userid = 0
    
    q = "select * from users where identifier='%s'" % (session.identifier)
    for r in db.query(q):
        session.userid = r.id
        
    if session.userid == 0:   
        session.userid = db.insert('users', identifier=session.identifier, name=session.name, email=session.email)

def SessionLogout():
    print "SessionLogout"
    session.loggedin = False
    session.identifier = ''
    session.name = ''
    session.email = ''
    session.userid = 0
    