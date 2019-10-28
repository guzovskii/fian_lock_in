import LpiCore.AutoCollectDevices as devices
import LpiCore.Experiment.BaseExperiment as module_experiment
import LpiCore.Utils as utils
import visa
import LpiCore.Gui as gui
import LpiCore.GlobalScope as module_global
import LpiCore.Logger as module_logger
import LpiCore.MySettings as module_settings
import os.path

##############################################################################################
if __name__ == '__main__':
    module_logger.MyLoggerConfigurator().Configure()
    rm = visa.ResourceManager()
    utils.list_all_visa_devices(rm=rm)
    experiment = None
    try:
        experiment = module_experiment.BaseExperiment()
        rm = visa.ResourceManager()
        settings = module_settings.MySettings(
            filename=os.path.join(os.path.dirname(__file__), "cfms_measurement_script.ini")
        )
        module_global.scope = module_global.GlobalScope(
            experiment=experiment,
            settings=settings,
        )
        #######################################################################
        auto_time = devices.TimeDevice(
            device_name="time",
            measure_labels={
                devices.TimeDevice.MEASURE_TIME: "time",
            }
        )
        experiment.AddNewDevice(auto_time)
        #######################################################################
        auto_sr = devices.AutoCollectSr830(
            rm=rm, address='COM3', device_name="sr",
            measure_labels={
                devices.AutoCollectSr830.MEASURE_R_THETA: "V",
                devices.AutoCollectSr830.MEASURE_FREQ: "f",
                devices.AutoCollectSr830.MEASURE_VOLT: "V_in",
            }
        )
        experiment.AddNewDevice(auto_sr)
        #######################################################################
        control_window = gui.ControlWindow()
        control_window.set_experiment(experiment)
        control_window.show()
        experiment.run()
    except Exception as e:
        print("Exception is:", e)
        raise
    except:
        print("Unknown exception")
    finally:
        if experiment:
            experiment.close()
            del experiment
        if experiment:
            experiment.close()
            del experiment
        rm.close()
        print("closing ALL")
