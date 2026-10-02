"""Run the local pilot. Build frontend first to serve the whole app on port 8000."""
import os
import sys
from pathlib import Path


def main():
    backend = Path(__file__).resolve().parent / 'backend'
    sys.path.insert(0, str(backend))
    print('Krishi Sahayak - local farmer workspace')
    print('Open http://127.0.0.1:8000')
    print('Demo accounts: farmer / farmer123, officer / officer123')
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=int(os.environ.get('PORT', '8000')),
                reload=os.environ.get('KRISHI_RELOAD') == '1')


if __name__ == '__main__':
    main()
