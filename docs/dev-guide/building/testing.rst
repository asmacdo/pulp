Testing the Build
-----------------

In order to test the build you have just made, you can publish it to the Pulp testing repositories.
Be sure to add the shared SSH keypair to your ssh-agent, and cd into the mash directory::

    $ ssh-add /path/to/key
    $ cd mash/
    $ rsync -avz --delete * pulpadmin@repos.fedorapeople.org:/srv/repos/pulp/pulp/testing/<X.Y>/

For our 2.4 beta example, the rsync command would be:

    $ rsync -avz --delete * pulpadmin@repos.fedorapeople.org:/srv/repos/pulp/pulp/testing/2.4/

You can now run the automated QE suite against the testing repository to ensure that the build is
stable and has no known issues. We have a Jenkins server for this purpose, and you can configure it
to test the repository you just published.
