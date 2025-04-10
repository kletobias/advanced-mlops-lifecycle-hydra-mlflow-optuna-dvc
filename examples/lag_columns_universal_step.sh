#!$ULOCAL/share/mamba/envs/ny/bin/python

python scripts/universal_step.py \
  setup.script_base_name=lag_columns \
  transformations=lag_columns \
  data_versions.data_version_input=v10 \
  data_versions.data_version_output=v11
