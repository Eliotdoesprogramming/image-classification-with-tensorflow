from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
import time
import os
import requests
import base64
import re
class myScraper(object):
    #initialize scraper with path to chromedriver
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = self.open_browser()


    #scrape bing for images on a certain topic
    def scrape_bing_for_images(self, search_term, number_of_images)->int:
        failcounter=0       
        self.driver.get("https://www.bing.com/images/search?q=" + search_term)
        image_src_paths = set()
        time.sleep(1)
        while(len(image_src_paths) < number_of_images):
            for path in self.grab_bing_image_src():       
                if(path not in image_src_paths):       
                    image_src_paths.add(path)

            if(self.scroll_down()):       
                failcounter = 0
            else:
                failcounter += 1
            if failcounter > 5:       
                break

            self.bing_seemore_button()
            print(len(image_src_paths),' image sources found')


        images_downloaded = self.download_images(search_term, image_src_paths)       
    
        return images_downloaded
            
        #scrape yahoo for images on a certain topic
    
    
    def scrape_yahoo_for_images(self,search_term, number_of_images):       
        failcounter=0       
        self.driver.get("https://images.search.yahoo.com/search/images?p=" + search_term)       
        image_src_paths = set()       
        time.sleep(1)       
        while(len(image_src_paths) < number_of_images):       
            for path in self.grab_yahoo_image_src():       
                if(path not in image_src_paths):       
                    image_src_paths.add(path)       
            if(self.scroll_down()):       
                failcounter = 0       
            else:       
                failcounter += 1       
            if failcounter > 5:       
                break       
            self.yahoo_seemore_button()       
            time.sleep(1)       
            print(len(image_src_paths),' image sources found')       
  
        images_downloaded = self.download_images(search_term, image_src_paths)  
        return images_downloaded+1

    def grab_yahoo_image_src(self):
        images = self.driver.find_elements_by_css_selector('li img')
        src_paths = []
        for image in images:
            src = image.get_attribute('src')
            if src != None:
                src_paths.append(src)
        return src_paths

    def yahoo_seemore_button(self):
        try:       
            more_button = self.driver.find_element_by_name('more-res')     
            more_button.click()
        except Exception as e:       
            print(e)
            return False
        return

    
    #scrape google for images on a certain topic 
    def scrape_google_for_images(self, search_term, number_of_images):       
        failcounter=0       
        self.driver.get("https://www.google.com/search?q=" + search_term)
        time.sleep(1)
        self.driver.find_element_by_link_text('Images').click()

        image_src_paths = set()       
        time.sleep(1)       
        while(len(image_src_paths) < number_of_images):       
            for path in self.grab_google_image_src():       
                if(path not in image_src_paths):       
                    image_src_paths.add(path)

            if(self.scroll_down()):       
                failcounter = 0       
            else:       
                failcounter += 1       
            if failcounter > 5:       
                break       
            self.google_seemore_button()       
            time.sleep(1)       
            print(len(image_src_paths),' image sources found')       
    
        number_of_images_downloaded = self.download_images(search_term, image_src_paths)
        
        
        return number_of_images_downloaded+1

    def google_seemore_button(self):       
            try:       
                more_button = self.driver.find_element_by_class_name('mye4qd')     
                more_button.click()
            except Exception as e:       
                print(e)

    def grab_google_image_src(self):
        images = self.driver.find_elements_by_class_name('rg_i')
        src_paths = []
        for image in images:
            src = image.get_attribute('src')
            if src != None:       
                src_paths.append(src)
        return src_paths

    #grab all of the image elements from the images with class mimg. then return a list of their src attributes
    def grab_bing_image_src(self):       
        images = self.driver.find_elements_by_class_name('mimg')
        src_paths = []
        for image in images:   
            src = image.get_attribute('src')
            #if not base64 image, continue
            if(src != None):       
                src_paths.append(src)
            
        return src_paths

    def full_screen_browser(self)->bool:       
        try:       
            self.driver.fullscreen_window()
            time.sleep(1)       
            return True       
        except:       
            return False

    def download_images(self, search_term, paths_to_save)->int:
        start_index = self.get_start_index(search_term)
        for idx, url in enumerate(paths_to_save):
            if(idx % 100 == 0):
                print(idx,' images downloaded')
            if (url[:4] != 'data'):
                self.download_image_from_url(url, self.driver_path[:-16]+'/images/'+str(search_term)+'/'+str(search_term[0:4])+str(idx+start_index)+'.png')
            elif(url[:4] == 'data'):       
                image_base64 = url.split('base64,')[1]
                format = 'jpeg' if url.split('image/')[1][0:4] == 'jpeg' else 'png'
                imgdata = base64.b64decode(image_base64)
                #write the base64 image to a file
                with open(self.driver_path[:-16]+'/images/'+str(search_term)+'/'+str(search_term[0:4])+str(idx+start_index)+'.'+format, 'wb') as f:
                    f.write(imgdata)
                    f.close()
        return idx

    def download_image_from_url(self, image_url, file_path):       
        response = requests.get(image_url)       
        with open(file_path, 'wb') as f:       
            f.write(response.content)       
        return

    def get_start_index(self, searchterm)->int:
        #if a directory doesnt exist for this search term, create it
        if not os.path.exists(self.driver_path[:-16]+'/images/'+str(searchterm)):
            os.makedirs(self.driver_path[:-16]+'/images/'+str(searchterm))

        images = os.listdir(self.driver_path[:-16]+'/images/'+str(searchterm))
        nums = []
        for image in images:
            if(image[-4:] == '.png' or image[-4:] == '.jpg'):
                try:
                    imgidx = re.search(r'\d+',image)[0]
                    nums.append(int(imgidx))
                except Exception as e:
                    print(e)
                    pass
        return 0 if len(nums)==0 else max(nums)
                
        

    def bing_seemore_button(self)->bool:
        try:
            seemore = self.driver.find_element_by_xpath('//*[@id="bop_container"]/div[2]/a')
        except Exception as e:
            print(e)
            print('couldnt find seemore button')
            return False
        if(seemore.is_displayed()):       
            seemore.click()       
            time.sleep(1)
            return True
        else:
            print("No seemore button found.")
            return False

    def scroll_down(self):
        #check window position
        scroll_position = self.driver.execute_script("return window.scrollY")
        self.driver.execute_script("window.scrollTo({left:0,top:(window.scrollY+1000),behavior:'smooth'});") 
        time.sleep(1) 
        #check to see if window position has changed
        new_scroll_position = self.driver.execute_script("return window.scrollY")
        
        return new_scroll_position != scroll_position
    #method to scroll up 200 pixels
    def scroll_up(self):
        self.driver.execute_script("window.scrollTo(0, -200);")
        time.sleep(1)
        return 
    def open_browser(self):
        driver = webdriver.Chrome(self.driver_path)
        return driver
    def close_browser(self):       
        self.driver.close()       
        self.driver.quit()       
        print("Browser closed.")       
        return

