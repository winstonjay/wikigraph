import unittest

from wikigraph import WikiGraph

top10pages = '''\
United States
Donald Trump
Barack Obama
India
World War II
Michael Jackson
Sex
United Kingdom
Lady Gaga
Eminem'''.split('\n')

samplepages = '''\
Turkey at the 1964 Summer Olympics
Olympics
Eurema sarilata
Variegated mountain lizard
Boerhaave
Tetrastrum
WordDive
Ashaga Fyndygan
derivatives
The Eagle (1925 film)
Bee
'''.split('\n')

class TestWikiGraph(unittest.TestCase):
    
    def test_find_path(self):
        '''Basic test to see if '''
        wiki_graph = WikiGraph()
        start, end = ('Tom Hanks', 'Will I Am')
        path = wiki_graph.find_path(start, end)

        self.assertEqual(path.start, start)
        self.assertEqual(path.end, end)
        self.assertTrue(path, "Path not found")
        self.assertTrue(len(path) < 6, "Path too long len=%d" % len(path))

    def test_find_path_benchmark(self):
        wiki_graph = WikiGraph(print_requests=True)
        total_requests = 0
        total_time = 0
        failures = []
        # Loop through and test if paths exit
        for page in samplepages:
            (start, end) = (page, "Homunculus")
            path = wiki_graph.find_path(start, end)
            if path.degree == -1:
                failures.append(path)
            total_requests += path.requests
            total_time += path.time

        print("Total Failures:", len(failures))
        print(failures)
        print("Total requests:", total_requests)
        print("Avg number of requests per path: %.2f" % (total_requests / len(top10pages)))
        print("Total time: ", total_time)
        print("Avg time per path: %.2f" % (total_time / len(top10pages)))








if __name__ == '__main__':
    unittest.main()