import undetected_chromedriver as uc
import os
import zipfile

def get_chromedriver():
    chrome_options = uc.ChromeOptions()
    
    # executable and binary locations
    # TODO: don't hardcode this
    chrome_options.binary_location = '/home/kenny/Builds/google-chrome/pkg/google-chrome/usr/bin/google-chrome-stable'        

    # proxy stuff
    # plugin_file = 'proxy_auth_plugin.zip'
    # with zipfile.ZipFile(plugin_file, 'w') as zip:
    #     zip.writestr('manifest.json', self.manifest_json)
    #     zip.writestr('background.js', self.background_js)
    # chrome_options.add_extension(plugin_file)    
    
    chrome_options.headless = True
    chrome_options.add_argument('--headless')

    prefs = {'profile.managed_default_content_settings.images': 2,
             'profile.managed_default_content_settings.javascript': 2,
             'profile.managed_default_content_settings.stylesheet': 2,
             'profile.managed_default_content_settings.css': 2}
    chrome_options.add_experimental_option('prefs', prefs)

    # TODO: don't hardcode this
    driver = uc.Chrome(executable_path='/home/kenny/Builds/chromedriver/src/chromedriver',
                       chrome_options=chrome_options)
    return driver
