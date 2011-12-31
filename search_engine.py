"""
    A toy search engine based on latent semantic indexing and singular value decomposition.
    
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
    
"""
import cPickle as pickle
import getopt
from numpy import arccos, dot, eye, resize, zeros
from numpy.linalg import inv, norm, svd
from sys import argv

class SearchEngine(object):
    """A toy search engine based on latent semantic indexing and singular value decomposition."""
    def __init__(self, data_file, no_svd_components, no_results):
        '''Constructs an instance of this class.
            Args:
                data_file: The path to a data file encoding page word counts, serialized using pickle.
                no_svd_components: The number of components to be used in truncated svd.
                no_results: The number of search results to return.
        '''
        data = loadData(data_file)
        self.urls, self.tags = extractData(data)
        self.no_tags = len(self.tags)
        A = generateCounts(data, self.urls, self.tags)
        normalize_columns(A)
        self.U, self.S, self.Vt = truncatedSVD(A, no_svd_components)
        self.Ut = self.U.T
        self.Si = inv(self.S)
        self.no_svd_components = no_svd_components
        self.no_results = no_results
   
    def build_query_vector(self, key_words):   
        '''Builds and returns a query vector based on the given list of key words.'''
        q = zeros(self.no_tags)
        for key in key_words:
            try:
                q[self.tags.index(key)] = 1
            except: pass
        return q
    
    def nearest_urls(self, qhat, no_results=None):   
        '''Builds and returns a list of urls ordered according to how close they
        are in the cosine distance to the given projected query vector.'''
        if not no_results: no_results = self.no_results
        cos_distances = []
        for i in xrange(len(self.urls)):
            cos_distances.append((i, cosDist(self.Vt[:,i], qhat)))
            cos_distances.sort(key=lambda x:x[1])
        return [self.urls[pair[0]] for pair in cos_distances[:no_results]]
   
    def project(self, q):   
        '''Returns the normalized projection onto document space of the given query vector.'''
        qhat = dot(self.Si, dot(self.Ut, q))
        qhat /= norm(qhat)
        return qhat
    
    def search(self, key_words):   
        '''Returns the search results for the given list of keywords.'''
        q = self.build_query_vector(key_words)
        qhat = self.project(q)
        return self.nearest_urls(qhat)

def loadData(data_file="lsiData.pkl"):
    '''Loads document word count data from the Python pickle file with the given relative path'''
    return pickle.load(open(data_file))

def cosDist(p, q): 
    '''Computes and returns the cosine distance between the given vectors.'''
    return arccos(dot(q, p)/(norm(q)*norm(p)))

def extractData(data):
    '''Extracts urls and tags from the given document word count data.'''
    urls = data.keys()
    urls.sort()
    tags = set()
    for tagfreq in data.values():
        tags.update(t for t, _ in tagfreq)
    tags = sorted(list(tags))
    return urls, tags

def generateCounts(data, urls, tags):
    '''Builds and returns a numpy array representing the term frequency matrix
    for the given data, urls and tags.'''
    A = zeros((len(tags), len(urls)))
    column = 0
    for url in urls:
        for tag, count in data[url]:
            row = tags.index(tag)
            A[row, column] = count
        column += 1
    return A

def normalize_columns(arr):
    '''Normalizes the given numpy array.'''
    rows, cols = arr.shape
    for col in xrange(cols):
        arr[:,col] /= norm(arr[:,col])

def truncatedSVD(A, k):
    '''Computes and returns a truncated SVD decomposition for the given matrix.'''
    U, S, Vt = svd(A)
    m, n = A.shape
    S = resize(S,[m,1])*eye(m,n)
    return U[:,:k], S[:k, :k], Vt[:k,:]

def usage():
    print "Usage:\n\tpython search_engine.py -f<input file> -n<number of svd components> -m<number of search results> <search key words>"
    
INPUT = "lsiData.pkl"
NUM_COMPONENTS = 10
NUM_RESULTS = 5
if __name__ == "__main__":    
    options, keywords = getopt.gnu_getopt(argv[1:], 'f:n:m:', ['input=', 'numcmp=', 'numres'])
    input = INPUT; numcmp = NUM_COMPONENTS; numres = NUM_RESULTS
    for opt, arg in options:
        try:
            if opt in ('-f', '--input'):
                input = arg
            elif opt in ('-n', '--numcmp'):
                numcmp = int(arg)
            elif opt in ('-m', '--numres'):
                numres = int(arg)
        except:
            usage()
            exit(2)
    if not keywords:
        print "No search keywords were given.  Using defaults.\n\n"
        keywords = ['australia']
        #keywords = ['animals', 'python']
    plural = ''
    if len(keywords) > 1: plural = 's'
    print "Results for search on keyword%s: %s" % (plural, ", ".join(keywords))
    engine = SearchEngine(input, numcmp, numres)
    print "\t%s" % "\n\t".join(engine.search(keywords))
        
