#!/usr/bin/env python

import web
from web import form
import json
from montecarlo import *
    
urls = (
  '/', 'projectlist',
  '/login', 'login',
  '/adduser', 'adduser',
  '/list', 'list',
  '/users', 'users',
  '/favicon.ico', 'favicon',
  '/montecarlo', 'montecarlo',
  '/projects', 'projects',
  '/projectlist', 'projectlist',
  '/project/(\d*)', 'project',
  '/project/(\d*)/tasks', 'tasks',
  '/project/(\d*)/edit', 'projectedit',
  '/project/(\d*)/delete', 'projectdelete',
  '/project/(\d*)/copy', 'projectcopy',
  '/project/(\d*)/results', 'results',
  '/project/(\d*)/report', 'projectreport'
)

render = web.template.render('templates/')
app = web.application(urls, globals())
db = web.database(dbn='sqlite', db='test.db')

loginForm = form.Form(
    form.Textbox('username'),
    form.Password('password'),
    form.Button('Login'),
)

signupForm = form.Form(
    form.Textbox('username'),
    form.Password('password'),
    form.Password('password_again'),
    form.Button('Signup'),
    validators = [form.Validator("Passwords didn't match.", lambda i: i.password == i.password_again)]
)

def RenderForm(form):
    return "<html><form name=\"main\" method=\"post\">%s</form></html>" % (form.render())
    
class favicon:
    def GET(self):        
        raise web.seeother('/static/favicon.ico')

def DumpTable(table):
    return json.dumps([t for t in db.select(table)])
    
def DumpQuery(q):
    return json.dumps([t for t in db.query(q)])
        
class list: 
    def GET(self):
        return DumpTable('todo')
        
class users:
    def GET(self):
        return DumpTable('users')
        
class projects:
    def GET(self):
        return DumpTable('projects')
        
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
            
        form += "<h1><a href=/project/%s/edit>%s</a></h1>" % (self.id, description)
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
        form = ProjectTable(id)
        return render.sim(id, form, 'none')    
        
class ProjectList:        
    def render(self):
        form = "<h1>Galton Projects</h1>\n" 
        form += "<table border=1 width=700px>\n"
        form += "<thead><tr><th>projects</th></tr></thead>\n"
        
        for r in db.query("select * from projects"):
            simURL = "<a href=/project/%s/report>%s</a>" % (r.id, r.description)
            editURL = "<a href=/project/%s/edit>edit</a>" % (r.id)
            form += "<tr><td>%s (%s)</td></tr>\n" % (simURL, editURL)            
            
        form += "</table>\n"
        
        form += "<form name=main method=post>\n"
        form += "<p><table border=1 width=700px>\n"
        form += "<tr><td>description: <input type=text name=desc size=60 maxlength=60 /> <button>Add New</button></td></tr>"
        form += "</table>\n"
        form == "</form>\n"
        
        return form
        
class projectlist:
    def GET(self):
        form = ProjectList()
        return render.form(form) 
        
    def POST(self):
        i = web.input()
        id = db.insert('projects', description=i.desc, estimate='p50', units='days', created=web.SQLLiteral("DATETIME('now','localtime')"), updated=web.SQLLiteral("DATETIME('now','localtime')"))
        db.insert('tasks', project=id, include=True, count=1, estimate=1.0, risk='medium', variance=0.55, description='task 1')
        raise web.seeother("/project/%d/edit" % (id))
        
def TextField(name, index, size, val):
    return """
        <td><input name="%s" id="%s_%d", type="text" size="%s" maxlength="%s" value="%s" onfocus="taskSim(%d);" onchange="taskSim(%d);"/></td>
        """ % (name, name, index, size, size, val, index, index)
        
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
            
        q = "select * from tasks where project=%s" % (self.id) 
        form += "<form name=main method=post>\n"
        form += """
            <table border=1 width=700px>
                <tr>
                    <th width=70px><a href="/project/%s/report">report</a></th><td colspan=2>project: <input name=project id=project size=60 value="%s" />
                    <td width=70px align=center><a href="/project/%s/copy">copy</a></td>
                </tr>
                <tr>
                    <th>estimate</th><td>type: %s</td><td>units: <input id=units name=units value="%s" /></td>
                    <td align=center><a href=/project/%s/delete>delete</a></td>
                </tr>
            </table><p/>""" % (self.id, desc, self.id, TypeField(type), units, self.id)
        form += "<table border=0 width=700px>\n"
        form += "<thead><tr><th width=70px>include</th><th>task</th><th>count</th><th>estimate</th><th>risk</th><th width=70px>delete</th></tr></thead>\n"
        index = 0
        for r in db.query(q):
            form += "<tr>\n"                            
            form += CheckboxField('include', index, r.include)
            form += TextField('desc', index, 30, r.description)
            form += TextField('count', index, 3, r.count)
            form += TextField('median', index, 5, r.estimate)
            form += RiskField(index, r.risk)
            form += CheckboxField('delete', index, False)
            form += "</tr>\n"
            
            index += 1
            
        for i in range(3):    
            form += "<tr>\n"
            form += CheckboxField('include', index+i, False)
            form += TextField('desc', index+i, 30, '')
            form += TextField('count', index+i, 3, '')
            form += TextField('median', index+i, 5, '')
            form += RiskField(index+i, '')
            form += "<td></td>\n"
            form += "</tr>\n"
            
        form += "</table>\n"
        form += "<button>Save</button>\n"
        form += "</form>\n"
        return form
    
def UpdateProject(id, wi, tasks):
    
    db.update('projects', where="id=%s" % (id), description=wi.project, estimate=wi.type, units=wi.units, updated=web.SQLLiteral("DATETIME('now','localtime')"))
    
    q = "delete from tasks where project=%s" % (id)
    db.query(q)
    for task in tasks:
        desc, count, median, risk, inc, rem = task
        if desc and median and risk and not rem:
            #print desc, median, risk, inc, rem
            var = RiskMap[risk]
            db.insert('tasks', project=id, description=desc, count=count, estimate=median, variance=var, risk=risk, include=inc)
        else:
            #print "invalid task", task
            pass
        
class projectedit:
    def GET(self, id):
        form = TaskForm(id)
        return render.sim(id, form, 'block')
        
    def POST(self, id):
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
        form = ProjectDeleteForm(id)
        print form.render()
        return render.form(form)
        
    def POST(self, id):
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
        form = ProjectCopyForm(id)
        print form.render()
        return render.form(form)
        
    def POST(self, id):
        q = "select * from projects where id=%s" % (id)
        for r in db.query(q):
            type = r.estimate
            units = r.units
            
        i = web.input()
        newId = db.insert('projects', description=i.desc, estimate=type, units=units)
        
        q = "select * from tasks where project=%s" % (id)
        with db.transaction():
            for r in db.query(q):
                db.insert('tasks', project=newId, include=r.include, count=r.count, estimate=r.estimate, risk=r.risk, variance=r.variance, description=r.description)
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
        
class results:
    def GET(self, id):
        i = web.input()

        try:
            trials = int(i.trials)
        except:
            trials = 10000
            
        q = "select * from projects where id=%s" % (id)
        for r in db.query(q):
            type = r.estimate
                    
        tasks = []
        q = "select * from tasks where project=%s" % (id)
        for r in db.query(q):
            if r.include:
                for i in range(int(r.count)):
                    task = Task(float(r.estimate), type, r.risk)
                    tasks.append(task)       
        results = RunMonteCarlo(trials,tasks)    
        return json.dumps(results)       
      
class login:
    def GET(self):
        form = loginForm()
        return RenderForm(form)
        
    def POST(self):
        form = loginForm()
        if form.validates():
            web.debug("valid form")
            q = db.query("select password from users where username='%s'" % (form.d.username))
            res = q[0]
            if res.password == form.d.password:
                return "user %s login OK" % (form.username.value)
            else:
                return "user %s login failed" % (form.username.value)
        else:
            return RenderForm(form)
            
class adduser:
    def GET(self):
        form = signupForm()
        return RenderForm(form)
        
    def POST(self):
        form = signupForm()
        if form.validates():
            web.debug("valid form")
            try:
                db.insert('users', username=form.d.username, password=form.d.password)
                return "user %s added OK" % (form.username.value)
            except:
                return "user %s failed" % (form.username.value)
        else:
            return RenderForm(form)
        
if __name__ == "__main__": 
    app.run()
        