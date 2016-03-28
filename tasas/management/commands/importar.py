from django.utils.translation import gettext as _
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.core.files import File

import json
import os
import warnings
import sys

from tasas.models import Universidad, Tasa, get_current_curso
import tasasrest.settings as settings

class Command(BaseCommand):
    help_text = _("Carga en la base de datos el fichero JSON utilizado en el proyecto original")

    def add_arguments(self, parser):
        """

        Args:
            parser: Instancia de [argparse](https://docs.python.org/3.5/library/argparse.html?highlight=argparse#module-argparse)

        Returns:
            None
        """
        parser.add_argument('file', type=str, help="Archivo json")
        parser.add_argument('img-dir', type=str, default='img/uni/',
                            help="Directorio con los logos de la universidad, siguiendo la convención uni_[siglas].jpg")
        parser.add_argument('--overwrite', action='store_true',
                            help="Sobreescribe la información de la base de datos", dest='overwrite')

    def handle(self, *args, **options):
        try:
            with open(options.get('file', ''), 'r') as f:
                data = json.load(f)
        except IOError:
            sys.stderr.write("Archivo '%s' no encontrado\n" % options.get('file', ''))
            return

        self.parse_file(data, options.get('img-dir'), options.get('overwrite', False))


    def parse_file(self, data, img_path='img/uni', overwrite=False):
        unis = data.get('unis', None)

        if unis is None or type(unis) is not list:
            raise CommandError(_("Archivo sin formato correcto"))\

        for uni in unis:
            try:
                self.add_uni(uni, img_path, overwrite)
            except ValidationError as v:
                sys.stderr.write("Error en clave: %s: %s" % (uni.get('siglas'), v))

    def parse_float(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0


    def add_uni(self, uni, img_path, overwrite=False):
        """
        Añade la universidad a la base de datos
        Args:
            uni: dict Diccionario con los datos de la universidad

        Returns:

        """
        try:
            universidad = Universidad.objects.get(siglas=uni.get('siglas'))
            if not overwrite: return
        except Universidad.DoesNotExist:
            universidad = Universidad()
        universidad.siglas = uni.get('siglas')
        universidad.nombre = uni.get('nombre')

        tipo = self.get_tipo_uni(uni.get('tipo'))
        
        if tipo is None:
            raise ValidationError("Tipo de universidad '%s' no válido para %s. Omitiendo." % (uni.get('tipo'), uni.get('nombre')))
            #return

        universidad.tipo = tipo
        universidad.centro = uni.get('centro')
        universidad.provincia = uni.get('provincia')
        universidad.campus = uni.get('campus')
        universidad.url = uni.get('url')

        if self.validate_logo(uni, img_path) is True:
            try:
                with open(os.path.join(img_path,
                                       'uni_%s.jpg' % Universidad.get_siglas_no_centro(uni.get('siglas'))), 'rb') as f:
                    logo = File(f)
                    universidad.logo.save('uni_%s.jpg' % Universidad.get_siglas_no_centro(uni.get('siglas')),
                                          logo, save=True)
            except IOError:
                warnings.warn("Error al abrir imagen %s" % uni+'.jpg')

        # TODO: Añadir convenios?
        universidad.clean_fields()
        universidad.save()

        self.add_tasas(uni, universidad)

    def validate_logo(self, uni, img_path):
        if uni.get('siglas', None) is None:
            sys.stderr.write("Siglas '%s' no válidas" % uni.get('siglas', ''))
            return

        if not os.path.isdir(img_path):
            sys.stderr.write("Directorio '%s' no válido" % img_path)
            return False

        return os.path.isfile(os.path.join(img_path,
                                           'uni_%s.jpg' % Universidad.get_siglas_no_centro(uni.get('siglas'))))


    def get_tipo_uni(self, tipo):
        """
        Retorna el valor asociado al tipo de universidad en la base de datos
        Args:
            tipo: Valor leído de fichero

        Returns:
            int
        """
        return next((code for code, value in dict(Universidad.TIPO_UNIVERSIDAD_CHOICES).items() if value == tipo), None)

    def add_tasas(self, data, uni):
        for year in range(settings.MIN_YEAR, get_current_curso()+settings.YEARS_IN_ADVANCE):
            tasa_data = data.get('tasas_%d' % year)
            if tasa_data is not None:
                tasa = Tasa()
                tasa.tipo = Tasa.PRECIO_POR_CREDITO
                tasa.tipo_titulacion = Tasa.GRADO
                tasa.curso = year

                tasa.tasas1 = self.parse_float(tasa_data.get('tasas1', 0))
                tasa.tasas2 = self.parse_float(tasa_data.get('tasas2', 0))
                tasa.tasas3 = self.parse_float(tasa_data.get('tasas3', 0))
                tasa.tasas4 = self.parse_float(tasa_data.get('tasas4', 0))

                tasa.url = tasa_data.get('url', None)

                tasa.universidad = uni

                try:
                    tasa.full_clean()
                    tasa.save()
                except ValidationError as v:
                    sys.stderr.write("Tasas de %s no válidas para universidad: %s: %s\n" %
                                     (year, uni.nombre, v.messages))

            else:
                sys.stderr.write("Tasas de %s no válidas para universidad: %s\n" % (year, uni.nombre))
