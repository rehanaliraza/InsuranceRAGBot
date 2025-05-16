#!/bin/zsh
# Reset environment to system Python

# Deactivate any active conda environments
if [[ -n $CONDA_PREFIX ]]; then
  echo "Deactivating conda environment..."
  conda deactivate
fi

# Remove miniconda from PATH
export PATH=$(echo $PATH | tr ':' '\n' | grep -v "miniconda" | tr '\n' ':' | sed 's/:$//')

# Verify system Python
echo "Current Python: $(which python) $(python --version 2>&1)"
echo "Current Python3: $(which python3) $(python3 --version 2>&1)"

