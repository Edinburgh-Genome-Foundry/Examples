# Templates

This directory contains Python notebook templates for DNA assembly design.

`template1.ipynb` is used for a standard assembly design workflow.

`template2_plan_update.ipynb`: GeneDom automatically shortens sequence names that are longer than 15 characters, and produces a file (`order_ids.csv`) as a lookup list for original and short names. We can use this file to update the part names in the assembly plan.

`template3_rename_parts_in_plan.ipynb`: this template is used for cases where we have an assembly plan with part names without position label prefixes (that are used by GeneDom). We can create an updated plan, using the ODS file and the notebook.
