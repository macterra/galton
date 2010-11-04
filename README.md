Galton : estimate with confidence
=================================

Projects are late more often than not because the people involved fail to take uncertainty into account.
Galton provides a simple interface to calculate confidence curves for risk-based estimation.

A project consists of any number of tasks. Each task has a description, an estimate of effort, 
and a risk (low, medium, high). Galton runs a monte carlo simulation on the tasks to derive a 
probability distribution of possible outcomes, then displays the confidence curve (cumulative 
distribution function) and related statistics (mode, median, mean, variance, etc).

Dependencies
------------

Galton depends on these python packages:

 * web.py
 * numpy
 
The data migration scripts depend on:

 * sqlalchemy
 * sqlalchemy-migrate
 

