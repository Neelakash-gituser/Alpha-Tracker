echo [$(date)]: 'START...'
echo [$(date)]: 'Creating Conda Env with Python 3.9'
conda create --prefix ./trader python=3.9 -y
echo [$(date)]: 'Activate Environment'
source activate ./trader
echo [$(date)]: 'Installing TA-LIB'
conda install -c conda-forge ta-lib -y
echo [$(date)]: 'Installing Requirements'
pip3 install -r requirements.txt
echo [$(date)]: '...Setup END'