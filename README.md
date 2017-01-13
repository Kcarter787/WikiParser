<b><h1>Challenge problem:</h1></b>

<b>Write a program using Python that performs the following:</b>    
  
Take any random article on Wikipedia (example: http://en.wikipedia.org/wiki/Art) and click on the first link
on the main body of the article that is not within parenthesis or italicized; If you repeat this process for each
subsequent article you will often end up on the Philosophy page.  
  
<b>Questions:</b>   
• What percentage of pages often lead to philosophy?  
• Using the random article link (found on any wikipedia article in the left sidebar),what is the distribution of
path lengths for 500 pages, discarding those paths that never reach the Philosophy page?  
• How can you reduce the number of http requests necessary for 500 random starting pages? 

<h2> How to use </h2>
-1.) Clone the project and install the modules listed in requirements.txt  
-2.) Set the desired number of starting urls and destination wiki page  
-3.) Run web_crawler.py  
-4.) Wait for the requests while monitoring the results* in the print log  
 *Statistics dont include calls made for external style sheets  
 ** For quicker results, ignore the italics requirement by simply returning false 
 for the is_italics function in crawler_objects.py
