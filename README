CONFIGURATION:
#############

You should read /etc/idleout/idleout.conf.example too.
The configuration file (/etc/idleout/idleout.conf) is divided into two sections.

1 ) logfile, pidfile and SMTP configurations.

2 ) Idle configurations.
This section is, at the same time, divided into two sections:

1 ) Group definitions.

2 ) User definitions.

These 2 sectors ALWAYS have to be in this order because user configurations have a higher magnitud than group configurations. 
So if a rule applies to a certain group but yo wish to apply another rule to a given user, the following user definitions will take care of this for you.

Each definition of the 2 sectors has 5 parameters:

(group|name)=group_name|user_name	idle=N (>=0)	grace=N	(>0)	mail=yes/no	silent=yes/no

1 ) Group or user definition.
2 ) Is the number of "minutes" that will apply to the first parameter. The value 0 means that the group or the user won't be checked for inactivity. 
    This number has to be in minutes (ie: 2hs = 120).
3 ) Is the number of grace minutes that will apply to the first parameter after the second one has been reached. 
    This number has to be > 0 (for know).
4 ) Send mail to user explaining why he was kicked out.
5 ) Define if the user should be notified to his screen or not. silent=no means NOTIFY.


WAYS TO USE IT:
##############
There are two ways to use it:

1 ) Starting it like an init service (/etc/init.d/idleout start).

2 ) Starting it from the terminal (/sbin/idleoutd).
    In this last option with -D or -d passed as an argument the application will print debugging info to the screen.

HOW IT WORKS:
############
Every 60 seconds the application takes a "snapshot" of the system users and based on the configuration file execute all the neceary work.
