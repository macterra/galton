#!/usr/bin/env python

import web

#web.config.debug = False

from web import form
import json
from montecarlo import *
from datetime import *
from time import mktime, strftime
import urllib, urllib2

import numpy
    
urls = (
  '/', 'projectlist',
  '/ng/', 'angular',
  '/login', 'login',
  '/logout', 'logout',
  '/users', 'users',
  '/favicon.ico', 'favicon',
  '/montecarlo', 'montecarlo',

  '/api/projects', 'GetProjects',
  '/api/project/(\d*)', 'GetProject',
  '/api/tasks/(\d*)', 'GetTasks',
  '/api/results/(\d*)', 'RunSimulation',
  '/api/project/save', 'SaveProject',

  '/projectlist', 'projectlist',
  '/project/(\d*)', 'project',
  '/project/(\d*)/tasks', 'tasks',
  '/project/(\d*)/edit', 'projectedit',
  '/project/(\d*)/delete', 'projectdelete',
  '/project/(\d*)/copy', 'projectcopy',
  '/project/(\d*)/results', 'results',
  '/project/(\d*)/resultscsv', 'resultscsv',
  '/project/(\d*)/schedule', 'schedule',
  '/project/(\d*)/report', 'projectreport'
)

render = web.template.render('templates/')
app = web.application(urls, globals())
db = web.database(dbn='sqlite', db='test.db')

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer=dict(loggedin=False))
    web.config._session = session
else:
    session = web.config._session
    
class angular:
    def GET(self):
        web.header('Content-Type', 'text/html')
        f = open('static/index.html', 'r')
        return f.read()

class favicon:
    def GET(self):        
        raise web.seeother('/static/favicon.ico')

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return strftime("%Y-%m-%d %H:%M", obj.timetuple())
        if isinstance(obj, date):
            return strftime("%Y-%m-%d", obj.timetuple())
        return json.JSONEncoder.default(self, obj)

def DumpTable(table):
    return json.dumps([t for t in db.select(table)], cls=MyEncoder)
    
def DumpQuery(q):
    return json.dumps([t for t in db.query(q)], cls=MyEncoder)
        
class users:
    def GET(self):
        return DumpTable('users')
        
class GetProjects:
    def GET(self):
        user = CurrentUser()
        q = """
            select p.*, u.name as owner,            
            case when p.userid=%d then 1 else 0 end as mine
            from projects p left outer join users u on p.userid=u.id
            where (p.publish=1 or p.userid=%d)
            order by updated desc
            """ % (user, user)
        return DumpQuery(q)

class GetProject:
    def GET(self, id):
        user = CurrentUser()
        id = int(id)
        q = """
            select p.*, u.name as owner,            
            case when p.userid=%d then 1 else 0 end as mine     
            from projects p left outer join users u on p.userid=u.id
            where (p.publish=1 or p.userid=%d) and p.id=%d
            """ % (user, user, id)
        return DumpQuery(q)

class GetTasks:
    def GET(self, id):
        user = CurrentUser()
        id = int(id)
        q = """
            select * from tasks where project=%d           
            """ % (id)
        return DumpQuery(q)
    
class RunSimulation:
    def GET(self, id):            
        return json.dumps(GetResults(id, 0))

class SaveProject:
    def POST(self):
        web.input() # init web.ctx.data
        p = json.loads(web.ctx.data)
        print web.ctx.data
        print p, type(p)        

        id = p['id']
        description = p['description']
        estimate = p['estimate']
        units = p['units']
        schedule = 1 if p['schedule'] else 0
        try:
            trials = int(p['trials'])

            if trials < 1:
                trials = 100
            if trials > 100000:
                trials = 100000
        except:
            trials = 10000

        try:
            capacity = float(p['capacity'])
        except:
            capacity = 1.0

        publish = 1 if p['publish'] else 0
        now = web.SQLLiteral("DATETIME('now','localtime')")

        db.update('projects', where="id=%d" % (id), 
                  description=description, 
                  estimate=estimate, 
                  units=units, 
                  publish=publish, 
                  schedule=schedule, 
                  trials=trials, 
                  capacity=capacity, 
                  updated=now)

        getProject = GetProject()
        return getProject.GET(id)

def CurrentUser():
    try:
        if session.loggedin:
            return session.userid
        else:
            return 0
    except:
        return 0    

def CheckOwner(id):
    q = "select * from projects where id=%s" % (id)
    for r in db.query(q):
        if CurrentUser() != r.userid:
            raise web.seeother("/")
            
class GreetingsForm():
    def render(self):
        try:
            #print session
            if session.loggedin:
                return """Welcome, %s <font color=white>[%d]</font> <a href="/logout">(Sign out)</a>""" % (session.name, session.userid)
        except:
            pass
        
        token_url = "%s/login" % (web.ctx.home)
        rpx_url = "https://galton.rpxnow.com/openid/v2/signin?token_url=%s" % (web.net.urlquote(token_url))
        return """<a class="rpxnow" onclick="return false;" href="%s"> Sign In </a>""" % (rpx_url)
 
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
    
class login:
    def GET(self):
        return session        
        
    def POST(self):
        i = web.input()
              
        api_params = {
            'token': i.token,
            'apiKey': '1f6c7a19c54ce28502d3e1e7ac7aebe732c9daf6',
            'format': 'json',
        }

        http_response = urllib2.urlopen('https://rpxnow.com/api/v2/auth_info', urllib.urlencode(api_params))
        auth_info_json = http_response.read()
        auth_info = json.loads(auth_info_json)
            
        if auth_info['stat'] == 'ok':
            SessionLogin(auth_info['profile'])
        else:
            SessionLogout()
            
        raise web.seeother("/")

class logout:
    def GET(self):
        SessionLogout()
        raise web.seeother("/")
        
class project:
    def GET(self, id):
        if not id:
            return DumpTable('projects')
        else:
            q = "select * from projects where id=%s" % (id)
            return DumpQuery(q)

class ProjectTable:
    def __init__(self, id):
        self.id = id
        
    def render(self):
        form = ""
        
        q = "select * from projects where id=%s" % (self.id)
        for r in db.query(q):
            description = r.description
            type = r.estimate
            units = r.units
            userid = r.userid
            
        if CurrentUser() == userid:    
            form += "<h1><a href=/project/%s/edit>%s</a></h1>" % (self.id, description)
        else:
            form += "<h1>%s</h1>" % (description)
            
        form += """<input type="hidden" id="project" value="%s"/>""" % (description)
        form += """<input type="hidden" id="type" value="%s"/>""" % (type)
        form += """<input type="hidden" id="units" value="%s"/>""" % (units)
            
        q = "select * from tasks where project=%s" % (self.id)
        form += "<table border=1>"
        form += "<thead><tr><th>task</th><th>count</th><th>estimate (%s)</th><th>risk</th></tr></thead>" % (type)
        for r in db.query(q):
            if r.include:
                form += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (r.description, r.count, r.estimate, r.risk)
        form += "</table>"
        return form
            
        
class projectreport:
    def GET(self, id):
        return render.sim(GreetingsForm(), id, ProjectTable(id), 'none')    
        
class ProjectList:        
    def render(self):
        form = "<table border=1 width=700px>\n"
        form += "<thead><tr><th>project</th><th>owner</th><th>created</th><th>updated</ht></tr></thead>\n"
        
        timestampFormat = "%Y-%m-%d %H:%M"
        
        q = "select p.*, u.name from projects p left outer join users u on p.userid=u.id order by updated desc"  
        
        for r in db.query(q):
        
            if CurrentUser() != r.userid and not r.publish:
                continue            

            created = r.created.strftime(timestampFormat)
            updated = r.updated.strftime(timestampFormat)                
            
            if CurrentUser() == r.userid:
                simURL = "<a href=/project/%s/report><b>%s</b></a>" % (r.id, r.description)
                editURL = "(<a href=/project/%s/edit>edit</a>)" % (r.id)
            else:
                simURL = "<a href=/project/%s/report>%s</a>" % (r.id, r.description)
                editURL = "(<a href=/project/%s/copy>copy</a>)" % (r.id)
            
            form += "<tr><td>%s %s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (simURL, editURL, r.name, created, updated)            
            
        form += "</table>\n"
        
        form += "<form name=main method=post>\n"
        form += "<p><table border=1 width=700px>\n"
        form += "<tr><td>description: <input type=text name=desc size=60 maxlength=60 /> <button>Add New</button></td></tr>"
        form += "</table>\n"
        form == "</form>\n"
        
        return form
        
class projectlist:
    def GET(self):
        return render.form(GreetingsForm(), ProjectList()) 
        
    def POST(self):
        i = web.input()
        id = db.insert('projects', description=i.desc, estimate='p50', units='days', userid=CurrentUser(), publish=False, created=web.SQLLiteral("DATETIME('now','localtime')"), updated=web.SQLLiteral("DATETIME('now','localtime')"))
        db.insert('tasks', project=id, include=True, count=1, estimate=1.0, risk='medium', description='task 1')
        raise web.seeother("/project/%d/edit" % (id))
        
def TextField(name, index, size, max, val):
    return """
        <td><input name="%s" id="%s_%d", type="text" size="%s" maxlength="%s" value="%s" onfocus="taskSim(%d);" onchange="taskSim(%d);"/></td>
        """ % (name, name, index, size, max, val, index, index)
        
def CheckboxField(name, val, checked):
    return """
        <td><input name="%s" type="checkbox" value="%s" %s /></td>
        """ % (name, val, "checked" if checked else "")

def RiskField(index, risk):    
    selected = ["selected" if risk == t else "" for t in ['none', 'low', 'medium', 'high', 'very high']]
    args = (index, index) + tuple(selected)
    
    return """
        <td>
            <select name="risk" id="risk_%d" onchange="taskSim(%s);">
                <option %s>none</option>
                <option %s>low</option>
                <option %s>medium</option>
                <option %s>high</option>
                <option %s>very high</option>
            </select>
        </td>            
        """ % args 

def TypeField(type):    
    selected = ["selected" if type == t else "" for t in ['mode', 'mean', 'p50', 'p80', 'p90']]
    
    return """
            <select name="type" id="type">
                <option value="mode" %s>most likely (mode)</option>
                <option value="mean" %s>average (mean)</option>
                <option value="p50" %s>50/50 (median)</option>
                <option value="p80" %s>80%% confident</option>
                <option value="p90" %s>90%% confident</option>
            </select>""" %  tuple(selected) 

class TaskForm:
    def __init__(self, id):
        self.id = id
        
    def render(self):
        form = ""
        
        q = "select * from projects where id=%s" % (self.id)
        for r in db.query(q):
            desc = r.description
            type = r.estimate
            units = r.units
            publish = r.publish
                
        form += "<form name=main method=post>\n"
        form += """
            <table border=1 width=700px>
                <tr>
                    <th width=70px><a href="/project/%s/report">report</a></th>
                    <td colspan=2>project: <input name=project id=project size=50 maxlength=60 value="%s" /> publish: <input type="checkbox" name="publish" %s /></td>
                    <td width=70px align=center><a href="/project/%s/copy">copy</a></td>
                </tr>
                <tr>
                    <th>estimate</th><td>type: %s</td><td>units: <input id=units name=units value="%s" /></td>
                    <td align=center><a href=/project/%s/delete>delete</a></td>
                </tr>
            </table><p/>""" % (self.id, desc, "checked" if publish else "", self.id, TypeField(type), units, self.id)
        form += "<table border=0 width=700px>\n"
        form += "<thead><tr><th width=70px>include</th><th>task</th><th>count</th><th>estimate</th><th>risk</th><th width=70px>delete</th></tr></thead>\n"
        index = 0
        
        q = "select * from tasks where project=%s" % (self.id) 
        for r in db.query(q):
            form += "<tr>\n"                            
            form += CheckboxField('include', index, r.include)
            form += TextField('desc', index, 30, 60, r.description)
            form += TextField('count', index, 3, 3, r.count)
            form += TextField('median', index, 5, 5, r.estimate)
            form += RiskField(index, r.risk)
            form += CheckboxField('delete', index, False)
            form += "</tr>\n"
            
            index += 1
            
        for i in range(3):    
            form += "<tr>\n"
            form += CheckboxField('include', index+i, False)
            form += TextField('desc', index+i, 30, 60, '')
            form += TextField('count', index+i, 3, 3, '')
            form += TextField('median', index+i, 5, 5, '')
            form += RiskField(index+i, '')
            form += "<td></td>\n"
            form += "</tr>\n"
            
        form += "</table>\n"
        form += "<button>Save</button>\n"
        form += "</form>\n"
        return form
    
def UpdateProject(id, wi, tasks):
    pub =  bool(wi.get('publish'))
    now = web.SQLLiteral("DATETIME('now','localtime')")
    db.update('projects', where="id=%s" % (id), description=wi.project, estimate=wi.type, units=wi.units, userid=CurrentUser(), publish=pub, updated=now)
    
    q = "delete from tasks where project=%s" % (id)
    db.query(q)
    for task in tasks:
        desc, count, median, risk, inc, rem = task
        if desc and median and risk and not rem:
            db.insert('tasks', project=id, description=desc, count=count, estimate=median, risk=risk, include=inc)
        
class projectedit:
    def GET(self, id):
        CheckOwner(id)
        return render.sim(GreetingsForm(), id, TaskForm(id), 'block')
        
    def POST(self, id):
        CheckOwner(id)
        wi = web.input(include=[], desc=[], count=[], median=[], risk=[], delete=[])
        #print wi
        inc = [int(x) for x in wi.include]
        rem = [int(i) for i in wi.delete] 
        all = range(len(wi.count))
        include = [x in inc for x in all]
        delete = [x in rem for x in all]
        tasks = zip(wi.desc, wi.count, wi.median, wi.risk, include, delete)
        UpdateProject(id, wi, tasks)
        raise web.seeother("/project/%s/edit" % (id))

class ProjectDeleteForm:
    def __init__(self, id):
        self.id = id
        
    def render(self):
        q = "select * from projects where id=%s" % (self.id)
        for r in db.query(q):
            desc = r.description
            
        form = """
            <form method="POST" onSubmit="return confirm('Deletion is permanent. Proceed?')">
                project: %s <button>Delete</button
            </form>""" % (desc)
            
        return form    
        
class projectdelete:
    def GET(self, id):
        CheckOwner(id)
        return render.form(GreetingsForm(), ProjectDeleteForm(id))
        
    def POST(self, id):
        CheckOwner(id)
        db.query("delete from tasks where project=%s" % (id))
        db.query("delete from projects where id=%s" % (id))
        raise web.seeother("/")
        
class ProjectCopyForm:
    def __init__(self, id):
        self.id = id
        
    def render(self):
        q = "select * from projects where id=%s" % (self.id)
        for r in db.query(q):
            desc = r.description
            
        form = """
            <p/>
            <form method="POST">
                <table border="1">
                <tr><td>project:</td><td>%s</td></tr>
                <tr><td>copy to:</td><td><input name="desc" type="text" size="60" maxlength="60" value="new name" /> <button>Copy</button></td></tr>
                </table>
            </form>""" % (desc)
            
        return form    
        
class projectcopy:
    def GET(self, id):
        return render.form(GreetingsForm(), ProjectCopyForm(id))
        
    def POST(self, id):
        q = "select * from projects where id=%s" % (id)
        for r in db.query(q):
            type = r.estimate
            units = r.units
            
        i = web.input()
        now = web.SQLLiteral("DATETIME('now','localtime')")
        newId = db.insert('projects', description=i.desc, estimate=type, units=units, userid=CurrentUser(), publish=False, created=now, updated=now)
        
        q = "select * from tasks where project=%s" % (id)
        with db.transaction():
            for r in db.query(q):
                db.insert('tasks', project=newId, include=r.include, count=r.count, estimate=r.estimate, risk=r.risk, description=r.description)
        raise web.seeother("/project/%d/edit" % (newId))
        
class tasks:
    def GET(self, id):
        q = "select * from tasks where project=%s" % (id)
        return DumpQuery(q)

class montecarlo:
    def GET(self):
        i = web.input()
        
        try:
            trials = int(i.trials)
        except:
            trials = 10000
            
        try:
            count = int(i.count)
        except:
            count = 1
            
        try:
            estimate = float(i.estimate)
        except:
            estimate = 1.0
            
        try:
            type = i.type
        except:
            type = 'p50'
            
        try:
            risk = i.risk
        except:
            risk = 'medium'
                        
        tasks = []
        for i in range(count):
            task = Task(estimate, type, risk)
            tasks.append(task)       
        results = RunMonteCarlo(trials,tasks)    
        return json.dumps(results)       
        
        
def GetResults(id, trials):
    q = "select * from projects where id=%s" % (id)
    for r in db.query(q):
        type = r.estimate

    if trials == 0:
        trials = r.trials

    schedule = r.schedule
    start = r.start
    capacity = r.capacity
                    
    tasks = []
    q = "select * from tasks where project=%s" % (id)
    for r in db.query(q):
        if r.include:
            for i in range(int(r.count)):
                task = Task(float(r.estimate), type, r.risk)
                tasks.append(task)   
                
    results = RunMonteCarlo(trials,tasks)

    if schedule:      
        effort, prob = zip(*results["cumprob"])
                
        cumprob = 0
        cumeffort = 0
        week = 0
        schedule = []
        
        while cumprob < 100:            
            cumprob = numpy.interp(cumeffort, effort, prob, 0, 100)
            #print week, cumeffort, cumprob           
            schedule.append([str(start), cumprob])                          
                
            cumeffort += capacity
            start += timedelta(7)
            week += 1
       
        #print schedule
        results["schedule"] = schedule
        
    return results
    
class results:
    def GET(self, id):
        i = web.input()

        try:
            trials = int(i.trials)
        except:
            trials = 10000
            
        return json.dumps(GetResults(id, trials))       
        
class resultscsv:
    def GET(self, id):
        i = web.input()

        try:
            trials = int(i.trials)
        except:
            trials = 10000
            
        results = GetResults(id, trials)
        
        pairs = ["%s,%s\n" % (pair[1], pair[0]) for pair in results["cumprob"]]
        return 'prob,effort\n' + ''.join(pairs)
    

class schedule:
    def GET(self, id):
        i = web.input()
        
        try:
            trials = int(i.trials)
        except:
            trials = 10000
            
        try:
            year, month, day = [int(x) for x in i.start.split('/')]
            start = date(year, month, day)
        except:
            start = date.today()
            
        try:
            velocities = [float(x) for x in i.velocity.split(',')]
        except:
            velocities = [1.]
            
        results = GetResults(id, trials)        
        effort, prob = zip(*results["cumprob"])
                
        cumprob = 0
        cumeffort = 0
        week = 0
        schedule = []
        
        while cumprob < 100:            
            cumprob = numpy.interp(cumeffort, effort, prob, 0, 100)
            #print week, cumeffort, cumprob           
            schedule.append([str(start), cumprob])
            
            if week < len(velocities):
                velocity = velocities[week]
            else:
                velocity = velocities[-1]                   
                
            cumeffort += velocity
            start += timedelta(7)
            week += 1
       
        #print schedule
        results["schedule"] = schedule          
        return json.dumps(results)
        
if __name__ == "__main__": 
    app.run()
        