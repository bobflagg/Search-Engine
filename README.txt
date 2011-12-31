This directory contains a Python code sample implementing a toy search engine 
based on latent semantic indexing and singular value decomposition.  The application
requires Python 2.6 or greater and the numpy library.  Also the Pickle file lsiData.pkl
must be in the same directory as the application or the path to a similarly encoded
word-document count file must be provided on the command line with the syntax
	-f<path-to-input-file>
    
Usage:
    
	python search_engine.py -f<input-file> -n<no-components> -m<no-results> <keywords>
        
		input-file: The path to a data file encoding page word counts, serialized using pickle.
		no-components: The number of components to be used in truncated svd.
		no-results: The number of search results to return.
		keywords: The keywords to search on.
            
On execution, a list of top-ranking pages for the given search keywords is printed to stdout.   
            
All input parameters are optional and set to reasonable default values if not given on the command line.
    
To run with defaults use:
	python search_engine.py
or
	python search_engine.py <keywords>
for example:
	python search_engine.py animals python
        
The most important parameter for determining the behavior of the search engine is no-components, which
specifies the number of components to be used in truncated svd. Large values will result in more
literal searches with little clustering of concepts.  Small values will result in large clusters
with few distinctions among keywords.  As shown in the scree plot (scree.jpg) an ideal choice for 
the number of components for the default data set is 10.

Bob Flagg
bob@calcworks.net
