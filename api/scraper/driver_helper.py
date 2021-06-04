import undetected_chromedriver as uc

class Driver:
    def __init__(self, proxy_host, proxy_port, proxy_username, proxy_password):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        manifest_json = """
        {
        "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                        "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
                ],
                "background": {
                        "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
            }
        };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """ % (proxy_host, proxy_port, proxy_username, proxy_password)
   
    def get_chromedriver():
        path = os.path.dirname(os.path.abspath(__file__))
        chrome_options = uc.ChromeOptions()
    
        # executable and binary locations
        # TODO: don't hardcode this
        options.binary_location = '/home/kenny/Builds/google-chrome/pkg/google-chrome/usr/bin/google-chrome-stable'        

        # proxy stuff
        plugin_file = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zip:
            zip.writestr('manifest.json', self.manifest_json)
            zip.writestr('background.js', self.background_js)
        chrome_options.add_extension(plugin_file)    

        # TODO: don't hardcode this
        driver = uc.Chrome(os.path.join(path, 'chromedriver'),
                           chrome_options=chrome_options,
                           exectuable_path='/home/kenny/Builds/chromedriver/src/chromedriver')
        return driver