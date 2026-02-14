"""
Admin utility functions for database backup and download
"""
from django.http import HttpResponse, Http404
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils import timezone
import os
import subprocess
import tempfile


@staff_member_required
def download_database(request):
    """
    Download database backup file.
    Supports both SQLite and PostgreSQL.
    """
    db_config = settings.DATABASES['default']
    db_engine = db_config['ENGINE']
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        if 'sqlite3' in db_engine:
            # SQLite - serve the database file directly
            db_path = db_config['NAME']
            
            if not os.path.exists(db_path):
                raise Http404("Database file not found")
            
            # Read the database file
            with open(db_path, 'rb') as db_file:
                response = HttpResponse(
                    db_file.read(),
                    content_type='application/x-sqlite3'
                )
                response['Content-Disposition'] = f'attachment; filename="aromas_db_{timestamp}.sqlite3"'
                return response
                
        elif 'postgresql' in db_engine:
            # PostgreSQL - create a dump file
            db_name = db_config['NAME']
            db_user = db_config['USER']
            db_password = db_config.get('PASSWORD', '')
            db_host = db_config.get('HOST', 'localhost')
            db_port = db_config.get('PORT', '5432')
            
            # Create temporary file for dump
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.sql')
            temp_file.close()
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            if db_password:
                env['PGPASSWORD'] = db_password
            
            # Run pg_dump
            pg_dump_cmd = [
                'pg_dump',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-d', db_name,
                '-F', 'c',  # Custom format (compressed)
                '-f', temp_file.name
            ]
            
            try:
                result = subprocess.run(
                    pg_dump_cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr or "Unknown error"
                    return HttpResponse(
                        f"Error creating database backup: {error_msg}",
                        status=500
                    )
                
                # Read the dump file
                with open(temp_file.name, 'rb') as dump_file:
                    response = HttpResponse(
                        dump_file.read(),
                        content_type='application/octet-stream'
                    )
                    response['Content-Disposition'] = f'attachment; filename="aromas_db_{timestamp}.dump"'
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                return response
                
            except subprocess.TimeoutExpired:
                os.unlink(temp_file.name)
                return HttpResponse("Database backup timed out. Please try again.", status=500)
            except FileNotFoundError:
                return HttpResponse(
                    "pg_dump not found. Please install PostgreSQL client tools.",
                    status=500
                )
            except Exception as e:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                return HttpResponse(f"Error: {str(e)}", status=500)
        else:
            return HttpResponse(
                f"Database engine {db_engine} is not supported for backup.",
                status=400
            )
            
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
