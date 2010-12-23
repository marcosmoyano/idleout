#!/bin/bash

#  Install the idleout daemon.
#  Marcos Moyano - marcos@gnu.org.ar

LOCAL="`pwd`"
BINDIR="/sbin/"
CONFDIR="/etc"
CONFFILE="$CONFDIR/idleout"
INITDIR="$CONFDIR/init.d/"
FILES="$LOCAL/src"
MAN="/usr/share/man/man1/"
#MAN="`echo $MANPATH | cut -d: -f 1`/man1/"

echo "Starting installation ... "
sleep 5
echo "Copying files ... "

if [ ! -f $INITDIR/idleout ]; then
	echo "Installing idleout --> $INITDIR/idleout"
	cp -f $FILES/idleout $INITDIR
	[ -x $INITDIR/idleout ] || chmod 755 $INITDIR/idleout
fi

if [ ! -f $BINDIR/idleoutd ]; then
	echo "Installing idleoutd --> $BINDIR/idleoutd"
	cp -f $FILES/idleoutd $BINDIR
	[ -x $BINDIR/idleoutd ] || chmod 744 $BINDIR/idleoutd
	echo "Installing usrout --> $BINDIR/usrout"
	cp -f $FILES/usrout $BINDIR
	[ -x $BINDIR/usrout ] || chmod 744 $BINDIR/usrout
fi

[ -d $CONFFILE ] || mkdir $CONFFILE

if [ ! -f $CONFFILE/idleout.conf ]; then
	echo "Installing idleout.conf --> $CONFFILE/idleout.conf"
	cp -f $FILES/idleout.conf $CONFFILE
	cp -f $FILES/idleout.conf.example $CONFFILE
fi

[ ! -d $MAN ] && mkdir $MAN
echo "Installing man (1) --> $MAN/idleoutd.1.gz"
echo "                   --> $MAN/usrout.1.gz"
cp -f man/idleoutd.1.gz $MAN
cp -f man/usrout.1.gz $MAN

echo "Installing README files --> $CONFFILE/"
cp -f doc/README.txt $CONFFILE/
cp -f doc/LEEME.txt $CONFFLE/

echo "Adding idleout to startup services ..."
sleep 5

$BINDIR/chkconfig --add idleout || echo -e "Error adding idleout to startup services.\n \
Please run: $BINDIR/chkconfig --add idleout "

echo "Finishing installation ... "
