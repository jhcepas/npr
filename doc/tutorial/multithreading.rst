Enabling Parallel computation
*******************************

Several layers of parallel computation are available

Enable multi-threading options in external software
======================================================

Certain steps of phylogenetic workflows may involve programs with
multi-threading capabilities (i.e. parallel computing). The maximum
number of threads per process can be defined in the **threading**
section of the config file. Multi-threading applications will consume
several CPU slots.


In the following example, raxml will be allowed to run using 16
threads, mattf using 4 and FastTree 3:

.. code-block:: ini

     [threading]

     raxml-pthreads = 16
     mafft = 4
     fasttree = 3


Note that: 

i) if the number of CPUs available is **higher** than the threading
limits, other task will be able to run in parallel with the
multi-threading application.

ii) if the number if CPUs available is **lower** than the threading
limits, applications will stick to the minimum number.

Local task distribution (Multi-core system)
=============================================

Many tasks in a phylogenetic workflow depend on each other. Other,
however, could be computed in parallel. ETE-NPR is fully aware of the
task tree of dependencies, meaning that, when more than 1 CPU is
available, independent tasks will be launched in parallel.

In example, if 5 evolutionary models are to be tested for the same
alignment, they will be launched at the same time as soon as 5 CPU
slots are available.

The maximum number of CPU slots can be defined in the command line
through the "-m" parameter.

.. code-block:: guess

      npr -m genetree -a AAseqs.fasta -o genetree_results/ -c MyConfig.cfg -x -m 16

Remote task distribution (cluster based execution)
======================================================

.. warning: 

   This is an experimental feature

Alternatively, heavy tasks could be submitted to a remote
cluster. Currently, only `Grid Engine` environments are fully
integrated, bindings to any other system can be easily implemented
through a `task execution hook function`.


Grid Engine
-----------------

Task execution hook function
----------------------------------

.. code-block:: python

  def task_execution_hook(command, config):
      print commands


