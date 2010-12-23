#!/usr/bin/env python

"""  Marcos Moyano - marcos@anue.biz

 Logout users of a specified period of idle time.

 Copyright (c) 2006 Marcos Moyano

 This program is free software; you can redistribute it and/or modify it
 under the terms of the GNU General Public License version 2 as published by
 the Free Software Foundation.
"""

__revision__ = "$Id: idleoutd 2007-6-11 $"
import os, sys, smtplib
from time import sleep
from re import compile as comp
from re import match
from logging import fatal, info, warning, DEBUG, getLogger, Formatter
from logging.handlers import RotatingFileHandler

G_FILE = "/etc/group"
P_FILE = "/etc/passwd"

### Necesary data ###
USR_BY_NAME = {}
GROUP_BY_NAME = {}
PROCS = {}
NO_BANN = []
BANN = {}
PRINTINFO = 0
PRINTVERSION = "0.8.1"
LOG_FLAG = 0

####################
# Manage arguments #
####################
if len(sys.argv[1:]) == 1:
    DEBUGG = sys.argv[1]
    if DEBUGG == "-D" or DEBUGG == "-d" or DEBUGG == "--debug":
        PRINTINFO = 1
    elif DEBUGG == "-h" or DEBUGG == "--help":
        printhelp()
        sys.exit(0)
    elif DEBUGG == "-v" or DEBUGG == "-V" or DEBUGG == "--version":
        print ("idleoutd version is: %s \n" % PRINTVERSION)
        sys.exit(0)
    else:
        print ("idleoutd: Invalid argument -- %s\n\
    Try 'idleoutd -h' or 'idleoutd --help' for more information." % DEBUGG)
        sys.exit(1)
elif len(sys.argv[1:]) > 1:
    print ("To many arguments: %d recieved, 1 expected.\n\
    Try 'idleoutd -h' or 'idleoutd --help'" % len(sys.argv[1:]))
    sys.exit(1)

#### End of manage arguments ####

##################
# Print Help Msg #
##################
def printhelp():
    """
    Print help information.
    """
    print """Logout users of a specified period of idle time.

Usage: idleoutd [OPTION]

   -D, -d, --debug          Print debug information to the screen every 60 seconds.
   -V, -v, --version        Print version information and exit.
   -h, --help               Print this help and exit.

Report bugs to <marcos@anue.biz>."""
    return

#### End of print help ####


######################
# Define logging way #
######################
def logg(LOG_FILE, LOG_SIZE):
    """
    Configuration of the log file.
    """
    RLOG = getLogger('')
    handler = RotatingFileHandler(LOG_FILE, 'a', LOG_SIZE * 1024 * 1024, 10)
    RLOG.addHandler(handler)
    RLOG.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s: %(levelname)-8s %(message)s','%b %d %H:%M:%S')
    handler.setFormatter(formatter)
    return

#### End of define logging ####

##################
# Get group info #
##################
def fetch_group(group, param):
    '''
    Fetch all the users in /etc/passwd with the same group id as "group".
    '''
    tmp = []
    gid = ""
    mygfile = open(G_FILE,'r')
    for lines in mygfile.readlines():
        line = lines.strip()
        name = line.split(':')[0]
        if group == name:
            gid = line.split(':')[2]
            break
    mygfile.close()
    mypfile = open(P_FILE,'r')
    for lines in mypfile.readlines():
        line = lines.strip()
        guid = line.split(':')[3]
        if gid == guid:
            tmp.append(line.split(":")[0])
    mypfile.close()
    GROUP_BY_NAME[group] = (tmp, param)
    return (GROUP_BY_NAME)

#### End of get group info ####

#################
# Group defined #
#################
def group_define(spar, param):
    """
    Fetch users from the specified group.
    """
    idle_time = param[0].split("=")[1]
    GROUP_BY_NAME = fetch_group(spar, param)
    try:
        filed = open(G_FILE,'r')
        for lines in filed.readlines():
            line = lines.strip()
            if spar == str(line.split(':')[0]):
                tmp = line.split(':')
                groups = tmp[len(tmp)-1]
        filed.close()
        lofusr = GROUP_BY_NAME[spar][0]
        groups = groups.split(',')
        for x in lofusr:
            if x not in groups:
                groups.append(x)
        if int(idle_time) == 0:
            for x in groups:
                if x not in NO_BANN:
                    NO_BANN.append(x)
                for y in GROUP_BY_NAME.keys():
                    if x in GROUP_BY_NAME[y][0]:
                        GROUP_BY_NAME[y] = (GROUP_BY_NAME[y][0][1:], param)
                    if GROUP_BY_NAME[y][0] == []:
                        del GROUP_BY_NAME[y]
        else:
            for usr in groups:
                if usr not in NO_BANN:
                    GROUP_BY_NAME[spar] = (groups, param)
    except Exception, err:
        warning("%s -> %s " % (err.__class__ , err))
        warning("I was unable to open file %s." % G_FILE)

#### end of group definded ####

################
# User defined #
################
def usr_define(spar, param):
    """
    Fetch the specified user.
    """
    try:
        filed = open(P_FILE,'r')
        for lines in filed.readlines():
            line = lines.strip()
            user = str(line.split(':')[0])
            if spar == user:
                itime = int(param[0].split('=')[1])
                if itime == 0:
                    if spar not in NO_BANN:
                        NO_BANN.append(spar)
                else:
                    if spar in NO_BANN:
                        NO_BANN.remove(spar)
                    USR_BY_NAME[spar] = param
        filed.close()
        if spar not in USR_BY_NAME.keys() and spar not in NO_BANN:
            info("Config file --> User %s is not defined in system." % spar)
    except Exception, err:
        warning("%s -> %s " % (err.__class__ , err))
        warning("I was unable to open file %s." % P_FILE)

#### end of user definded ####

##################
#    Get info    #
##################
def get_info(LOG_FLAG):
    """
    Parse the configuration file.
    """
    try:
        from idleoutconf import log, logsize, pid, host, port, domain
        from idleoutconf import group, name
        if LOG_FLAG != 1:
            logg(log, int(logsize))
            # Don't open another logging instance!
            LOG_FLAG = 1
        global smtp
        smtp = [host, int(port), domain]
        reg1 = comp('(\s+)\=(\s+)')
        for users in name:
            users = reg1.sub("=", users.strip())
            usrtmp = users.split()
            usrname = usrtmp[0]
            rest = usrtmp[1:]
            usr_define(usrname, rest)
        for groups in group:
            groups = reg1.sub("=", groups.strip())
            grtmp = groups.split()
            groupname = grtmp[0]
            rest = grtmp[1:]
            group_define(groupname, rest)
        return(pid)
    except Exception, err:
        print >> sys.stderr, "Error: %d: %s" % (err.errno, err.strerror)
        sys.exit(err.errno)

#### end get info ####

##################
#  Compute info  #
##################
def compute(process):
    """
    Manage all the information and call the require events.
    """
    tmp = [x for x, y in BANN.iteritems() if x not in process.keys()]
    for x in tmp:
        del BANN[x]             	# Clean people who got back
    for x, y in process.iteritems():
        user = x.split(',')[0]
        dev = x.split(',')[1]
        time = int(y[0])
        # Search in user define dictionary
        if USR_BY_NAME.has_key(user):
            idtm = int(USR_BY_NAME[user][0].split('=')[1])
            if time >= idtm:
                grace = int(USR_BY_NAME[user][1].split('=')[1])
                silent = USR_BY_NAME[user][3].split('=')[1]
                if x in BANN.keys():
                    if BANN[x] >= grace:
                        del BANN[x]
                        if silent == "no":
                            bann_usr(x, y[1], grace, 0)  # Bann the user
                        else:
                            # Bann the user with silent
                            bann_usr(x, y[1], grace, 1)
                        mail = USR_BY_NAME[user][2].split('=')[1]
                        if mail == "yes":
                            send_mail(user, dev)
                    else:
                        BANN["%s" % x] = int(BANN[x]) + 1
                else:
                    ret = checkcon(x)
                    if ret == 0:
                        BANN["%s" % x] = 1
                        if silent == "no":
                            notify(user, dev, grace)   # Notify the user
                    else:
                        # No ssh session - Banning with silent
                        bann_usr(x, y[1], grace, 1)
            else:
                if x in BANN.keys():
                    del BANN[x]
        else:
            """
            Group search:
            We'll grab the lowest idle configuration available. In addition we'll grab the
            corresponding grace and mail configuration for that particular user.
            By default we set the mail configuration to "no". If it needs to change it will do so.
    	    """
        # Big number just to make sure idle time is lower in the first run
            loweridt = 1000
            lowgrace = 0
            lowmail = "no"
            silent = "no"
        # Search in group define dictionary for the lowest idle time.
            for j, k in GROUP_BY_NAME.iteritems():
                if user in k[0]:
                    idtm = int(GROUP_BY_NAME[j][1][0].split('=')[1])
                    if idtm < loweridt:
                        loweridt = idtm
                        lowgrace = int(GROUP_BY_NAME[j][1][1].split('=')[1])
                        lowmail = GROUP_BY_NAME[j][1][2].split('=')[1]
                        silent = GROUP_BY_NAME[j][1][3].split('=')[1]
            if time >= loweridt:
                if x in BANN.keys():
                    if BANN[x] >= lowgrace:
                        del BANN[x]
                        if silent == "no":
                            bann_usr(x, y[1], lowgrace, 0)  # Bann the user
                        else:
                        # Bann the user with silent
                            bann_usr(x, y[1], lowgrace, 1)
                        if lowmail == "yes":
                            send_mail(user, dev)
                    else:
                        BANN["%s" % x] = int(BANN[x]) + 1
                else:
                    ret = checkcon(x)
                    if ret == 0:
                        BANN["%s" % x] = 1
                        if silent == "no":
                            notify(user, dev, lowgrace)   # Notify the user
                    else:
                        bann_usr(x, y[1], lowgrace, 1)
            else:
                if x in BANN.keys():
                    del BANN[x]

#### End of compute ####

##################
#   Notify user  #
##################
def notify(user, dev, grace):
    """
    Notify the user that he is going to be kicked out.
    """
    fdr = "/dev/"+dev
    seconds = grace*60
    try:
        tonot = open(fdr,'a')
        tonot.write("\n\r\n<<< MESSAGE FROM IDLEOUT >>>\n\n\
        \r\tYou have been idle for too long.\n\
        \r\tIf you don't send an alive signal in the next %d seconds you will be kicked out!\n\n\
\r<<<    END OF MESSAGE    >>>\n\n" % seconds)
        tonot.close()
        warning("USER %s idle on DEVICE %s --> NOTIFYING!" % (user, dev))
    except Exception, err:
        warning("%s -> %s " % (err.__class__ , err))
        warning("I was unable to open device %s." % fdr)

#### end of notify user ####

##########################
#  check ssh connection  #
##########################
def checkcon(info):
    """
    Look for the sshd process of the specified user in the specified device.
    """
    user = info.split(',')[0]
    device = info.split(',')[1]
    sshd = os.popen("ps -ef | grep %s | grep %s | grep sshd | grep -v \"grep\" | head -n 1" % (device, user), 'r')
    sshd = sshd.read()
    if sshd:
        sshd = sshd.strip().split()
    else:
        warning("USER %s not on DEVICE %s --> KICKING OUT!" % (user, device))
        return (1)
    if sshd[5] == "?" and sshd[7] == "sshd:":
        if sshd[8].strip() == "%s@%s" % (user.strip(), device.strip()):
            return (0) # Found ssh session
        else:
            return (1) # There is no ssh session for the user in the device.

#### End of checkcon ####

###############
#  Bann user  #
###############
def bann_usr(user, pids, seconds, silent):
    """
    Kick out the specified user.
    """
    usr = user.split(',')[0]
    device = user.split(',')[1]
    seconds = int(seconds)*60
    fdr = "/dev/"+device
    warning("USER %s --> timeout on DEVICE %s --> KICKING OUT!" % (usr, device))
    if int(silent) == 0:
        try:
            tonot = open(fdr,'a')
            tonot.write("\n\r\n<<< MESSAGE FROM IDLEOUT >>> \n\n\
	    \r\tYour %s seconds has expired.\n\
	    \r\tKicking out user: %s\n\n\
\r<<<    END OF MESSAGE    >>>\n\n" % (seconds, usr))
            tonot.close()
        except Exception, err:
            warning("%s -> %s " % (err.__class__ , err))
            warning("I was unable to open device %s." % fdr)
    for process in pids.split():
        process = int(process)
        try:
            os.kill(process, 9)
        except Exception, e:
            warning("%s -> %s " % (e.__class__ , e))
            warning("Process don't exist or error killing it (%d)" % process)

#### End of bann user ####

#############
# Get pids  #
#############
def get_pids(idle_pos, name_pos, dev_pos):
    """
    Find the idle info and processes of the users currently logged in.
    """
    PROCS = {}
    info1 = os.popen("finger | cut -c %s,%s,%s | sed 1d | egrep -v \"\*:0\" | sort | uniq" % (name_pos, dev_pos, idle_pos), "r")
    for line in info1:
        c = line.split()
    # Added to check differences between distros. Distros like SuSE use this.
        if "*" == c[1][0]:
            c[1] = c[1][1:]
        if c[0] not in NO_BANN:
            if len(c) == 3:
                try:
                    t = int(c[2])
                except ValueError:
                    if ":" in c[2]:
                        t = c[2].strip()
                        t = int(t.split(':')[0])*60 + int(t.split(':')[1])
                    elif "d" in c[2]:
                        t = c[2].strip()
                        t = int(t)*60*24
                lo = os.popen("ps -eo \"%s\" | awk '{print $3 \" \" $1 \" \" $2}' | grep %s | grep %s | egrep -v \"grep\" | awk '{print $2}' | xargs" % ("%p %y %U", c[0], c[1]), "r")
                for li in lo.readlines():
                    li = li.strip()
                    info("USER: %s --> DEVICE: %s --> IDLE TIME: %s --> PROCESSES: %s" % (c[0], c[1], str(t), li))
                    PROCS["%s,%s" % (c[0], c[1])] = (t, li)
    return(PROCS)

#### end of get_pids ####

##########################
# Check for SMTP service #
##########################
def check_smtp():
    """
    Check for the SMTP service.
    """
    try:
        server = smtplib.SMTP(smtp[0], smtp[1])
    except Exception, err:
        warning("%s -> Exit code %s -> Message: %s" % (err.__class__ , err[0], err[1]))
        return(1)
    server.quit()
    return(0)

#### end of check SMTP ####

#############
# Send mail #
#############
def send_mail(user, dev):
    """
    Send an email to the specified user explaining the situation.
    """
    ecode = check_smtp()
    if ecode != 0:
        warning("An SMTP error ocurred. NOT sending email.")
        return
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    domain = smtp[2]
    if domain.lower() != "none":
        toaddrs  = "%s@%s" % (user, domain)
        fromaddr = "%s@%s" % ("idleout", domain)
    else:
        toaddrs  = user
        fromaddr = "idleout"
    line = "You have been idle for too long.\n\
    Idleout has decided to terminate your conection on device %s.\n" % dev
    msg = ("From: %s\r\nTo: %s\r\n\r\n%s" % (fromaddr, toaddrs, line))
    try:
        server = smtplib.SMTP(smtp[0], smtp[1])
        server.set_debuglevel(0)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
        info("Email sent to user %s" % user )
    except Exception, err:
        warning("%s -> Exit code %s -> Message: %s" % (err.__class__ , err[0], err[1]))
        warning("An SMTP error ocurred. NOT sending email.")

#### end of send_mail ####

#####################
# Get Idle position #
#####################
def get_pos():
    '''
    Function to find the locations of "Name", "Tty" and "Idle" from the finger command.
    '''
    idle = os.popen("finger | head -n 1", "r")
    line = idle.readline().strip()
    tmp = line.find("Idle") + 1
    idle_pos = str("%d-%d" % (tmp - 1, tmp + 4))
    tmp = line.find("Name")
    name_pos = str("%d-%d" % (1, tmp))
    tmp = line.find("Tty")
    dev_pos = str("%d-%d" % (tmp, tmp + 7))
    return(idle_pos, name_pos, dev_pos)

#### End of get_pos ####

####################
# Print debug info #
####################
def prinfo(PROCS, usr_name, group_name, nobann, ybann, smtp):
    """
    Print the DEBUG information.
    """
    print "                  <<<<< DEBUG MODE >>>>> "
    print "---------------------------------------------------------"
    print "      <<< SMTP DIRECTIVES FROM CONFIG FILE >>>\n"
    host = smtp[0]
    port = smtp[1]
    domain = smtp[2]
    print ("HOST: %s --> PORT: %d --> DOMAIN: %s" % (host, port, domain))
    print "---------------------------------------------------------"
    print "      <<< USER DIRECTIVES FROM CONFIG FILE >>>"
    for name in usr_name.keys():
        print ("USER: %s " % name)
        tmp = " ".join(usr for usr in usr_name[name])
        print ("CONFIGURATION: %s" % tmp)
    print "---------------------------------------------------------"
    print "      <<< GROUP DIRECTIVES FROM CONFIG FILE >>>"
    for group in group_name.keys():
        print ("GROUP: %s" % group)
        tmp = " ".join(usr for usr in group_name[group][0])
        tmp1 = " ".join(conf for conf in group_name[group][1])
        print ("USERS IN GROUP: %s" % tmp)
        print ("CONFIGURATION: %s" % tmp1)
        print "---------------------------------------"
    tmp = " ".join(usr for usr in nobann)
    print "---------------------------------------------------------"
    print ("USERS THAT WILL NEVER BE KICKED OUT: %s" % tmp)
    print "---------------------------------------------------------"
    print "IDLE USERS: "
    for info in PROCS.keys():
        user = info.split(',')[0]
        dev = info.split(',')[1]
        time = PROCS[info][0]
        print ("USER: %s --> DEVICE: %s --> IDLE TIME: %s" % (user, dev, time))
    print "---------------------------------------------------------"
    print "      <<< PROCESSES OF IDLE USERS: >>>\n"
    for info in PROCS.keys():
        user = info.split(',')[0]
        dev = info.split(',')[1]
        pro = PROCS[info][1]
        print ("USER: %s --> DEVICE: %s --> PROCESSES: %s" % (user , dev, pro))
    print "---------------------------------------------------------"
    print "<<< GRACE: USERS THAT WILL (eventually) BE KICKED OUT >>>\n"
    for info in ybann.keys():
        user = info.split(',')[0]
        dev = info.split(',')[1]
        gra = ybann[info]
        print ("USER: %s --> DEVICE: %s --> GRACE MINUTE: %s" % (user, dev, gra))
    print "\n#########################################################"
    print "            <<< Sleeping for 60 seconds >>> "
    print "#########################################################\n"

#### End of prinfo ####

###########
#  MAIN   #
###########
def main():
    """
    Main function.
    """
    try:
        count = 1
    # Just at the beginning to get positions in finger.
    #These positions changes between distros.
        (id_pos, name_pos, dev_pos) = get_pos()
        while True:
            if count == 30:
                count = 1
        # Read conf file at start and every 30 minutes
                get_info(LOG_FLAG)
            else:
                count = count + 1
            PROCS = get_pids(id_pos, name_pos, dev_pos)
            try:
                compute(PROCS)
            except Exception, err:
                warning("%s -> %s " % (err.__class__ , err))
            if PRINTINFO == 1:
                prinfo(PROCS, USR_BY_NAME, GROUP_BY_NAME, NO_BANN, BANN, smtp)
            sleep(60) # Sleep for 60 seconds
    except:
        print "Signal caught. Exiting!"
        sys.exit(1)

#### End of MAIN :) ####

if __name__ == "__main__":
    try:
        sys.path.append('/etc/idleout')
        LOG_FLAG = 0
        pidfile = get_info(LOG_FLAG)
    except Exception, err:
        print ("%s -> %s " % (err.__class__ , err))
        sys.exit(1)
    info("<<< Starting Idleout daemon >>>")
    try:
        import psyco   # try to speed up :)
        psyco.full()
    except ImportError:
        info("Psyco is not installed, the program will just run a bit slower")
        pass
    if PRINTINFO == 1:
        info("<<< Idleout daemon started in debug mode >>>")
        main()
    else:
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0) # exit first parent
        except OSError, e:
            print >> sys.stderr, "fork 1 failed: %d (%s)" % (e.errno, e.strerror)
            fatal("I was unable to fork into a deamon")
            sys.exit(1)
        try:
            os.chdir("/")
        except Exception, err:
            info("%s -> %s " % (err.__class__ , err))
            pass
        try:
            os.setsid()
        except Exception, err:
            info("%s -> %s " % (err.__class__ , err))
            pass
        try:
            os.umask(0)
        except Exception, err:
            info("%s -> %s " % (err.__class__ , err))
            pass
        try:
            pid = os.fork()
            if pid > 0:
                myfile = open(pidfile, 'w')
                myfile.write(str(pid) + '\n')
                myfile.close()
                info("<<< Idleout daemon started - Pid: %s >>>" % str(pid))
                sys.exit(0)
        except OSError, err:
            print >> sys.stderr, "fork 2 failed: %d: %s" % (err.errno, err.strerror)
            fatal("I was unable to fork into a deamon")
            sys.exit(1)
# Start the daemon
        main()
