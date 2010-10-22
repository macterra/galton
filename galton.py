import web
from web import form
import json
import time
from numpy import *
from random import *

class Task:
    def __init__(self, median, sigma):
        self.p50 = median
        self.sigma = sigma
        self.mode = median / math.exp(sigma*sigma)

    def Time(self): 
        return self.p50 * lognormvariate(0,self.sigma)
     
def RunMonteCarlo(trials, tasks):
    t = time.time()
    times = ([])
    n = 0
    
    if trials > 100000:
        print "RunMonteCarlo: too many trials", trials
        trials = 10000
        
    if trials < 1:
        trials = 10000
        
    for x in xrange(trials):
        sum = 0
        for task in tasks:
            sum += task.Time()
        times = append(times,sum)
    elapsed = time.time() - t
    times = sort(times)
    N = len(times)
    cumprob = [[times[t*N/100], t] for t in range(100)]
    results = dict(simtime=elapsed, trials=trials, cumprob=cumprob, mean=times.mean(), std=times.std(), risk=log(times).std());
    return results
    
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
  '/project/(\d*)/results', 'results',
  '/project/(\d*)/run', 'projectrun'
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
            
        form += "<h1>%s <a href=/project/%s/edit>(edit)</a></h1>" % (description, self.id)
        form += """<input type="hidden" id="project" value="%s"/>""" % (description)
            
        q = "select * from tasks where project=%s" % (self.id)
        form += "<table border=1 width=50%>"
        form += "<thead><tr><th>task</th><th>count</th><th>median</th><th>variance</th></tr></thead>"
        for r in db.query(q):
            if r.include:
                form += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s (%s)</td></tr>" % (r.description, r.count, r.median, r.variance, r.risk)
        form += "</table>"
        return form
            
class projectrun:
    def GET(self, id):
        form = ProjectTable(id)
        return render.sim(id, form)    
        
class ProjectList:        
    def render(self):
        form = "<h1>Galton Projects</h1>\n" 
        form += "<table border=1 width=50%>\n"
        form += "<thead><tr><th>projects</th></tr></thead>\n"
        
        for r in db.query("select * from projects"):
            simURL = "<a href=/project/%s/run>%s</a>" % (r.id, r.description)
            editURL = "<a href=/project/%s/edit>edit</a>" % (r.id)
            form += "<tr><td>%s (%s)</td></tr>\n" % (simURL, editURL)            
            
        form += "</table>\n"
        
        form += "<form name=main method=post>\n"
        form += "<p><table border=1 width=50%>\n"
        form += "<tr><td>description: <input type=text name=desc size=60 /> <button>Add New</button></td></tr>"
        form += "</table>\n"
        form == "</form>\n"
        
        return form
        
class projectlist:
    def GET(self):
        form = ProjectList()
        return render.form(form) 
        
    def POST(self):
        i = web.input()
        id = db.insert('projects', description=i.desc)
        db.insert('tasks', project=id, include=True, count=1, median=1.0, risk='medium', variance=0.55, description='task 1')
        raise web.seeother("/project/%d/edit" % (id))
        
def TextField(name, index, size, val):
    return """
        <td><input name="%s" id="%s_%d", type="text" size="%s" value="%s" onfocus="taskSim(%d);" onchange="taskSim(%d);"/></td>
        """ % (name, name, index, size, val, index, index)
        
def CheckboxField(name, val, checked):
    return """
        <td><input name="%s" type="checkbox" value="%s" %s /></td>
        """ % (name, val, "checked" if checked else "")

def RiskField(index, risk):
    noneSelected = "selected" if risk == "none" else ""
    lowSelected = "selected" if risk == "low" else ""
    mediumSelected = "selected" if risk == "medium" else ""
    highSelected = "selected" if risk == "high" else ""
    veryHighSelected = "selected" if risk == "very high" else ""
    
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
        """ % (index, index, noneSelected, lowSelected, mediumSelected, highSelected, veryHighSelected)

class TaskForm:
    def __init__(self, id):
        self.id = id
        
    def render(self):
        form = ""
        
        q = "select * from projects where id=%s" % (self.id)
        for r in db.query(q):
            desc = r.description
            
        q = "select * from tasks where project=%s" % (self.id) 
        form += "<form name=main method=post>\n"
        form += """
            <table border=1 width=50%%>
                <tr>
                    <th><a href="/project/%s/run">project</a></th><td><input name=project id=project size=60 value=\"%s\" />
                    <td><a href=/project/%s/delete>delete</a></td>
                </tr>
            </table><p/>""" % (self.id, desc, self.id)
        form += "<table border=0 width=50%>\n"
        form += "<thead><tr><th>include</th><th>task</th><th>count</th><th>median</th><th>risk</th><th>delete</th></tr></thead>\n"
        index = 0
        for r in db.query(q):
            form += "<tr>\n"                            
            form += CheckboxField('include', index, r.include)
            form += TextField('desc', index, 20, r.description)
            form += TextField('count', index, 5, r.count)
            form += TextField('median', index, 5, r.median)
            form += RiskField(index, r.risk)
            form += CheckboxField('delete', index, False)
            form += "</tr>\n"
            
            index += 1
            
        for i in range(3):    
            form += "<tr>\n"
            form += CheckboxField('include', index+i, False)
            form += TextField('desc', index+i, 20, '')
            form += TextField('count', index+i, 5, '')
            form += TextField('median', index+i, 5, '')
            form += RiskField(index+i, '')
            form += "<td></td>\n"
            form += "</tr>\n"
            
        form += "</table>"
        form += "<button>Save</button>\n"
        form += "</form>\n"
        return form

RiskMap = { 'none' : 0.01, 'low' : 0.27, 'medium' : 0.54, 'high' : 0.81, 'very high' : 1.08 }
    
def UpdateProject(id, description, tasks):
    
    db.update('projects', where="id=%s" % (id), description=description)
    
    q = "delete from tasks where project=%s" % (id)
    db.query(q)
    for task in tasks:
        desc, count, median, risk, inc, rem = task
        if desc and median and risk and not rem:
            #print desc, median, risk, inc, rem
            var = RiskMap[risk]
            db.insert('tasks', project=id, description=desc, count=count, median=median, variance=var, risk=risk, include=inc)
        else:
            print "invalid task", task
        
class projectedit:
    def GET(self, id):
        form = TaskForm(id)
        return render.sim(id, form)
        
    def POST(self, id):
        wi = web.input(include=[], desc=[], count=[], median=[], risk=[], delete=[])
        print wi
        inc = [int(x) for x in wi.include]
        rem = [int(i) for i in wi.delete] 
        all = range(len(wi.count))
        include = [x in inc for x in all]
        delete = [x in rem for x in all]
        tasks = zip(wi.desc, wi.count, wi.median, wi.risk, include, delete)
        UpdateProject(id, wi.project, tasks)
        raise web.seeother("/project/%s/edit" % (id))

class ProjectDeleteForm:
    def __init__(self, id):
        self.id = id
        
    def render(self):
        q = "select * from projects where id=%s" % (self.id)
        for r in db.query(q):
            desc = r.description
            
        form = """
            <form method="POST" onSubmit="return confirm('Delete for realz?')">
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
            trials = 1
            
        try:
            median = float(i.median)
        except:
            median = 1.0
            
        try:
            risk = i.risk
        except:
            risk = 'medium'
         
        try:
            var = RiskMap[risk]
        except:
            var = RiskMap['medium']
        
        tasks = []
        for i in range(count):
            task = Task(median, var)
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
            
        tasks = []
        q = "select * from tasks where project=%s" % (id)
        for r in db.query(q):
            if r.include:
                for i in range(int(r.count)):
                    task = Task(float(r.median), float(r.variance))
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
        