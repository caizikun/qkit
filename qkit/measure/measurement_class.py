# MP, AS @ KIT 05/2017
# Class to collect all information about a single measurement

import logging
import json, types
import os, copy
import qkit.core.qt as qt
from qkit.config.environment import cfg
from qkit.measure.json_handler import QkitJSONEncoder, QkitJSONDecoder
from qkit.measure.samples_class import Sample

class Measurement(object):
    '''
    Measurement class to define general information about the specific measurement.
    '''
    def __init__(self):
        self.uuid = None
        self.hdf_relpath = ''
        self.sample = None
        self.web_visible = True
        self.rating = 3
        self.analyzed = False
        self.measurement_type = ''
        self.measurement_func = ''
        self.x_axis = ''
        self.y_axis = ''
        self.z_axis = ''
        self.instruments = None
        self.user = cfg.get('user','John_Doe').strip().replace(" ","_")
        self.run_id = cfg.get('run_id','NO_RUN')

    def get_JSON(self):
        """
        Returns JSON string of all attributes. The function is mostly used for saving in .h5.
        """
        return json.dumps(obj=self._get_copydict(), cls=QkitJSONEncoder, indent = 4, sort_keys=True)

    def save(self,filepath=None):
        '''
        Save sample object in the same directory as the measurement .h5 file or in the given filepath.
        '''
        if filepath:
            filepath=filepath
        else:
            filepath = os.path.join(qt.config.get('datadir'),self.hdf_relpath.replace('.h5', '.measurement'))

        with open(filepath,'w+') as filehandler:
            json.dump(obj=self._get_copydict(), fp=filehandler, cls=QkitJSONEncoder, indent = 4, sort_keys=True)

    def load(self, filename):
        '''
        Load sample keys and entries to current sample instance.
        '''
        if not os.path.isabs(filename):
            filename = os.path.join(qt.config.get('datadir'),filename)

        with open(filename) as filehandle:
            self.__dict__ = json.load(filehandle, cls = QkitJSONDecoder)

        s = Sample()
        s.__dict__ = self.__dict__['sample']
        self.__dict__['sample'] = s
    
    def _get_copydict(self):
        '''
        Returns a copy of self.__dict__ with all object attributes returned in a JSONable format.
        '''
        copydict = copy.copy(self.__dict__)

        """
        Both 'sample' and 'instruments' entries have to be converted into a dict to save information about datatype etc.
        """
        if copydict['sample']:
            copydict['sample'] = copydict['sample'].__dict__ # change entry to dict to make it readable for JSONEncoder
        if copydict['instruments']:
            if type(copydict['instruments']) is not types.DictType: # conversion needed during measurement
                copydict['instruments'] = self._JSON_instruments_dict()
        return copydict
            
    def _JSON_instruments_dict(self):
        '''
        Iterates through all entries in the self.instruments dict and creates a dict with the individial instrument
        name together with all attributs, attribute values and information about setter function. This is needed
        for an automized reading and re-setting of a measurement.
        '''
        return_dict = {}
        for ins_name in self.instruments:
            ins = self.instruments[ins_name]
            param_dict = {}
            for param_name in ins.get_parameter_names():
                has_setter = 'set_func' in ins.get_parameter_options(param_name)
                param_dict.update({param_name:{'content':ins.get(param_name, query=False), 'has_setter':has_setter}})
            return_dict.update({ins_name:param_dict})
        return return_dict

    def update_instrument(self, ins_name):
        '''
        Sets all parameters of the instrument ins_name to the values used in the measurements.
        '''
        try:
            ins = qt.instruments.get(ins_name)
            params_dict = self.instruments['instruments'][ins_name]
        except AttributeError or NameError:
                logging.error('Relevant instruments and attributes not properly specified.')
        else:
            '''
            Use only parameters with setter and update the instrument
            '''
            for param in params_dict.keys():
                if params_dict[param]['has_setter']: ins.set(params_dict[param], params_dict[param]['content'])
    
    def update_all_instruments(self):
        '''
        Updates all instruments to their parameter settings during the measurement.
        CAUTION: This can be critical for current sources, since the current value is set and not ramped!
        '''
        for ins in self.instuments:
            self.update_instrument(ins)
            