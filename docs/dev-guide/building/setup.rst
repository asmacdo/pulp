What you will need
^^^^^^^^^^^^^^^^^^

In order to build Pulp, you will need the following from the Foreman team:

#. An account on Foreman's Koji instance
#. A client certificate for your account
#. The Katello CA certificate

See the `Foreman Wiki <http://projects.theforeman.org/projects/foreman/wiki/Koji>`_ to get these
items.

In order to publish builds to the Pulp repository, you will need the SSH keypair used to upload
packages to the fedorapeople.org repository. You can get this from members of the Pulp team.

Additionally you will need to install ``createrepo`` on the machine you will be building from.

Configuring your build environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are interested in building Pulp, it is strongly recommended that you use a separate checkout
from your normal development environment to avoid any potential errors such as building in local
changes, or building the wrong branches. It is also a good idea to use a build host in a location
with good outbound bandwidth, as the repository publish can be at or over 250 MB. Thus, the first
step is to make a clean checkout of the pulp_packging somewhere away from your other checkouts::

    $ mkdir ~/pulp_build
    $ cd ~/pulp_build
    $ git clone git@github.com:pulp/pulp_packaging.git

The next step is to install and configure the Koji client on your machine. You will need to put the
Katello CA certificate and your client certificate in your home folder::

    $ sudo yum install koji

Here is an example $HOME/.koji/config file you can use::

    [koji]

    ;configuration for koji cli tool

    ;url of XMLRPC server
    server = http://koji.katello.org/kojihub

   ;url of web interface
    weburl = http://koji.katello.org/koji

    ;url of package download site
    topurl = http://koji.katello.org/

    ;path to the koji top directory
    ;topdir = /mnt/koji

    ;configuration for SSL athentication

    ;client certificate
    cert = ~/.katello.cert

    ;certificate of the CA that issued the client certificate
    ca = ~/.katello-ca.cert

    ;certificate of the CA that issued the HTTP server certificate
    serverca = ~/.katello-ca.cert

Make sure you install your Katello CA certificate and client certificate to the paths listed in the
example above::

    $ cp <katello CA> ~/.katello-ca.cert
    $ cp <katello client cert> ~/.katello.cert

If all went well, you should be able to say hello to Koji::

    $ [rbarlow@notepad]~% koji moshimoshi
    olá, rbarlow!

    You are using the hub at http://koji.katello.org/kojihub

Next, you should install Tito::

    $ sudo yum install tito

Now you are ready to begin building.
