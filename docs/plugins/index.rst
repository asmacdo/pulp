Plugins
=======

Pulp Core is incomplete without plugins, it does not manage content by itself. Each content type
must be provided by a plugin. Examples of a content type include a RPM package, Ansible role, or
Docker container.

Features that can be added by a plugin include:

* Defining a new content type
* Fetching content from an external repository
* Publishing content, allowing Pulp Core to serve it via https or http. Often, publications provide
  the information necessary for a client (like pip or dnf) to interact with a set of content.
* Exporting content, including pushing to remote servers or the creation of ISOs.
* Implementing custom features, e.g. dependency solving, retension/deletion policies, etc.
* Adding custom web application views, allowing a plugin to implement arbitrary APIs, including
  live APIs.

For example, the `file_plugin <https://github.com/pulp/pulp_file>`_ adds support fo managing files.

All known Pulp plugins are listed below. If you are interested in creating a plugin, see
:doc:`TODO(asmacdo) these docs <plugin-writer/index>`.

And don't hesitate to :ref:`contact us<community>` with any questions during planning or
development. Let us know when the plugin is ready and we will add it to the list of available
plugins!


.. _plugin-table:

Plugin List
-----------

.. list-table::
   :header-rows: 1
   :widths: auto
   :align: center

   * - Pulp Plugin
     - Docs
     - Source
     - Tracker
     - Install with PyPI
     - Install with RPM

   * - File
     - `File plug-in docs <https://github.com/pulp/pulp_file/blob/master/README.rst>`_
     - `File plug-in source <https://github.com/pulp/pulp_file>`_
     - `File plug-in tracker <https://pulp.plan.io/projects/pulp_file?jump=welcome>`_
     - Yes
     - No

   * - Ansible plug-in
     - `Ansible plug-in docs <https://github.com/pulp/pulp_ansible/blob/master/README.rst>`_
     - `Ansible plug-in source <https://github.com/pulp/pulp_ansible>`_
     - `Ansible plug-in tracker <https://pulp.plan.io/projects/ansible_plugin?jump=welcome>`_
     - No
     - No

   * - Python plug-in
     - `Python plug-in docs <http://pulp-python.readthedocs.io/en/latest/>`_
     - `Python plug-in source <https://github.com/pulp/pulp_python/tree/3.0-dev>`_
     - `Python plug-in tracker <https://pulp.plan.io/projects/pulp_python?jump=welcome>`_
     - Yes
     - No

.. note::
   Are we missing a plugin? Let us know via the pulp-dev@redhat.com mailing list.

.. toctree::
   plugin-writer/index
   plugin-api/overview
