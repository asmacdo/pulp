Signing the RPMS
----------------

Get the signing key
^^^^^^^^^^^^^^^^^^^
Before signing RPMs, you will need access to the Pulp signing key. Someone on
the Pulp team can provide you with this. Additionally you should be familiar
with the concepts in the `Creating GPG Keys
<https://fedoraproject.org/wiki/Creating_GPG_Keys>`_ guide.

All alpha, beta and GA RPMs should be signed with the Pulp team's GPG key. A
new key is created for each X release (3.0.0, 4.0.0, etc).  If you are doing a
new X release, a new key needs to be created. To create a new key, run ``gpg
--gen-key`` and follow the prompts. We usually set "Real Name" to "Pulp (3)"
and "Email address" to "pulp-list@redhat.com". Key expiriation should occur
five years after the key's creation date. After creating the key, export both
the private and public keys.  The public key should be saved as
``GPG-RPM-KEY-pulp-3`` and the private as ``pulp-3.private.asc``. The password
can go into ``pulp-3-password.txt``.  Please update ``encrypt.sh`` and
``decrypt.sh`` as well to include the new private key and password file. Run
``encrypt.sh`` to encrypt the new keys.

.. warning::

   If you are making an update to the key repo, be sure to always verify that
   you are not committing the unencrypted private key or password file!

.. note::

   If you are adding a new team member, just add their key to ``encrypt.sh``
   and ``decrypt.sh``, then re-encrypt the keys and commit. The new team member
   will also need to obtain the "sign" permission in koji.

The ``GPG-RPM-KEY-pulp-3`` file should be made available under
https://repos.fedorapeople.org/repos/pulp/pulp/.


Existing X Stream
^^^^^^^^^^^^^^^^^

If you are simply creating a new build in an existing X stream release, you
need to perform some one-time setup steps in your local environment. First,
create or update your ``~/.rpmmacros`` file to include content like so,
substituting X with your intended release::

    %_gpg_name Pulp (X)



Sign the rpms
^^^^^^^^^^^^^

Using the password stored in the text file, run the following from your mash directory::

    $ find -name "*.rpm" | xargs rpm --addsign

This will sign all of the RPMs in the mash. You then need to import signatures into koji::

   $ find -name "*.rpm" | xargs koji import-sig

.. note::

   Koji does not store the entire signed RPM. It merely stores the additional
   signature metadata, and then re-creates a signed RPM in a different
   directory when the ``write-signed-rpm`` command is issued. The original
   unsigned RPM will remain untouched.

As ``list-signed`` does not seem to work, do a random check in
http://koji.katello.org/packages/ that
http://koji.katello.org/packages/<name>/<version>/<release>/data/sigcache/<sig-hash>/
exists and has some content in it. Once this is complete, you will need to
tell koji to write out the signed RPMs (both commands are run from your mash dir)::

   $ for r in `find -name "*src.rpm"`; do basename $r; done | sort | uniq | sed s/\.src\.rpm//g > /tmp/builds
   $ for x in `cat /tmp/builds`; do koji write-signed-rpm <SIGNATURE-HASH> $x; done

Sync down your mash one more time (run from the ``pulp_packaging/ci`` dir)::

   $ ./build-all.py <release_config> --disable-push --rpmsig <SIGNATURE-HASH>

.. note::

   This command does not download signed RPMs for RHEL 5, due to bugs in RHEL 5
   related to signature verification. While we sign all RPMs including RHEL 5, we
   do not publish the signed RPMs for this particular platform.

After it is synced down, you can publish the build.
