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
  '/project/(\d*)/results', 'results',
  '/test/(\d*)', 'test'
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
        
class test:
    def GET(self, id):
        return render.test(id)
        
class tasks:
    def GET(self, id):
        q = "select * from tasks where project=%s" % (id)
        return DumpQuery(q)
        
class results:
    def GET(self, id):
        tasks = []
        q = "select * from tasks where project=%s" % (id)
        for r in db.query(q):
            task = Task(r.mean, r.variance)
            tasks.append(task)       
            #web.debug("task mode=%f, var=%f, p50=%f, time=%f" % (task.mode, task.sigma, task.p50, task.Time()))
        results = RunMonteCarlo(50000,tasks)    
        return json.dumps(results)
        
    def POST(self, id):
        return GET(id)
        
    def OPTIONS(self, stuff):
        print stuff
        return stuff
      
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
        