.. _getsource:

Get the Source
==============

It is assumed that any Pulp project repositories are cloned into one directory. As long as Ansible has read and write permissions, it doesn't matter where your **development directory** is.

.. note::

    The git repositories required by each role are documented in :ref:`ansible-roles`.

You will need ``pulp/devel`` and ``pulp/pulp`` at a minimum::

    $ git clone https://github.com/pulp/devel.git
    $ git clone https://github.com/pulp/pulp.git

If you are using ``pulp-from-source.yml``, that is all you will need. If your playbook includes optional :ref:`ansible-roles`, you may require additional repositories::

    $ git clone https://github.com/PulpQE/pulp-smash.git
    $ git clone https://github.com/pulp/pulpproject.org.git

If you want to use the ``plugin`` role, you'll also need to clone the plugin repository.::

    $ git clone https://github.com/pulp/pulp_file.git

.. warning::

    It is important to ensure that your repositories are all checked out to compatible versions.
