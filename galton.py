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
  '/', 'index',
  '/login', 'login',
  '/adduser', 'adduser',
  '/list', 'list',
  '/users', 'users',
  '/projects', 'projects',
  '/project/(\d*)', 'project',
  '/project/(\d*)/tasks', 'tasks',
  '/project/(\d*)/edit', 'projectedit',
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
    
class index:
    def GET(self):        
        return "Hello, world!"

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
            form = "<h1>project: %s</h1>" % (r.description)
            
        q = "select * from tasks where project=%s" % (self.id)
        form += "<table border=1 width=50%>"
        form += "<thead><tr><th>task</th><th>count</th><th>median</th><th>variance</th></tr></thead>"
        for r in db.query(q):
            if r.include:
                form += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (r.description, r.count, r.mean, r.variance)
        form += "</table>"
        form += "<a href=/project/%s/edit>edit tasks</a>" % (self.id)
        return form
            
class projectrun:
    def GET(self, id):
        form = ProjectTable(id)
        return render.test(id, form)    
        
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
        form += "<table border=0>\n"
        form += "<tr><th>project</th><td><input name=\"project\" size=40 value=\"%s\" /></td></tr>" % (desc)
        form += "</table><p>"
        form += "<table border=0 width=50%>\n"
        form += "<thead><tr><th>include</th><th>task</th><th>count</th><th>median</th><th>variance</th><th>delete</th></tr></thead>\n"
        index = 0
        for r in db.query(q):
            form += "<tr>\n"
                            
            form += "<td><input name=\"include\" type=\"checkbox\" value=\"%s\" %s /></td>\n" % (index, "checked" if r.include else "")
            form += "<td><input name=\"desc\" type=\"text\" value=\"%s\" /></td>\n" % (r.description)
            form += "<td><input name=\"count\" type=\"text\" value=\"%s\" /></td>\n" % (r.count)
            form += "<td><input name=\"mean\" type=\"text\" value=\"%s\" /></td>\n" % (r.mean)
            form += "<td><input name=\"var\" type=\"text\" value=\"%s\" /></td>\n" % (r.variance)
            form += "<td><input name=\"delete\" type=\"checkbox\" value=\"%s\" /></td>\n" % (index)
            form += "</tr>\n"
            
            index += 1
            
        for i in range(3):    
            form += "<tr>\n"
            form += "<td><input name=\"include\" type=\"checkbox\" value=\"%s\" /></td>\n" % (index+i)
            form += "<td><input name=\"desc\" type=\"text\" value=\"\" /></td>\n" 
            form += "<td><input name=\"count\" type=\"text\" value=\"\" /></td>\n"
            form += "<td><input name=\"mean\" type=\"text\" value=\"\" /></td>\n"
            form += "<td><input name=\"var\" type=\"text\" value=\"\" /></td>\n"
            form += "<td></td>\n"
            form += "</tr>\n"
        form += "</table>"
        form += "<button>Submit</button>\n"
        form += "</form>\n"
        form += "<a href=/project/%s/run>run sim</a>" % (self.id)
        return form

def UpdateProject(id, description, tasks):
    db.update('projects', where="id=%s" % (id), description=description)
    
    q = "delete from tasks where project=%s" % (id)
    db.query(q)
    for task in tasks:
        desc, count, mean, var, inc, rem = task
        if desc and mean and var and not rem:
            print desc, mean, var, inc, rem
            db.insert('tasks', project=id, description=desc, count=count, mean=mean, variance=var, include=inc)
        else:
            print "invalid task", task
        
class projectedit:
    def GET(self, id):
        form = TaskForm(id)
        return render.simple(form)
        
    def POST(self, id):
        wi = web.input(project='', include=[], desc=[], count=[], mean=[], var=[], delete=[])
        #print wi
        inc = [int(x) for x in wi.include]
        rem = [int(i) for i in wi.delete] 
        all = range(len(wi.count))
        include = [x in inc for x in all]
        delete = [x in rem for x in all]
        tasks = zip(wi.desc, wi.count, wi.mean, wi.var, include, delete)
        UpdateProject(id, wi.project, tasks)
        raise web.seeother("/project/%s/edit" % (id))
        
class tasks:
    def GET(self, id):
        q = "select * from tasks where project=%s" % (id)
        return DumpQuery(q)
        
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
                    task = Task(float(r.mean), float(r.variance))
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
        