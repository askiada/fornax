import unittest
import fornax.api
import fornax.model
from test_base import TestCaseDB
from sqlalchemy.orm.session import Session


class TestGraph(TestCaseDB):

    @classmethod
    def setUp(self):
        # trick fornax into using the test database setup
        super().setUp(self)
        fornax.api.Session = lambda: Session(self._connection)

    def test_init_raises(self):
        """ raise an ValueError if a hadle to a graph is constructed that does not exist """
        self.assertRaises(ValueError, fornax.api.Graph, 0)
        self.assertRaises(ValueError, fornax.api.Graph.read, 0)

    def test_create(self):
        graph = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))
        self.assertEqual(graph.graph_id, 0)

    def test_non_edges(self):
        self.assertRaises(
            ValueError,
            fornax.api.Graph.create,
            range(5), 
            zip(range(2), range(2))
        )

    def test_assert_int_edges(self):
        self.assertRaises(
            ValueError,
            fornax.api.Graph.create,
            range(5), 
            (('a', 'b'), ('c', 'd'))
        )

    def test_assert_int_node_id(self):
        self.assertRaises(
            ValueError,
            fornax.api.Graph.create,
            ('a', 'b', 'c'), 
            []
        )

    def test_count(self):
        """ len(graph) should count the nodes in a graph """
        N = 5
        graph = fornax.api.Graph.create(range(N), [])
        self.assertEqual(len(graph), N)

    def test_yield_nodes(self):
        self.assertListEqual(
            list(fornax.api.Graph.create([1,2,3], [(1, 2), (2, 3)]).nodes()),
            [1, 2, 3]
        )

    def test_yield_edges(self):
        edges = [(1, 2), (2, 3)]
        self.assertListEqual(
            sorted(fornax.api.Graph.create([1,2,3], edges).edges()),
            edges
        )

    def test_delete(self):
        graph = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))
        graph.delete()
        self.assertEqual(len(self.session.query(fornax.model.Node).all()), 0)
        self.assertEqual(len(self.session.query(fornax.model.Edge).all()), 0)

    def test_delete_exists(self):
            graph = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))
            graph.delete()
            self.assertRaises(ValueError, graph.delete)

    def test_increment_id(self):
        graphs = [fornax.api.Graph.create(range(5), zip(range(2), range(2,5))) for i in range(3)]
        self.assertListEqual([g.graph_id for g in graphs], [0, 1, 2])


class TestQuery(TestCaseDB):

    @classmethod
    def setUp(self):
        # trick fornax into using the test database setup
        super().setUp(self)
        fornax.api.Session = lambda: Session(self._connection)

    def test_match_start_raises(self):

        graph_a = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))
        graph_b = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))
        self.assertRaises(
            ValueError,
            fornax.api.Query.create,
            graph_a,
            graph_b,
            [('a', 1, 1), (1, 2, 1), (2, 2, 1)]
        )   

    def test_match_end_raises(self):

        graph_a = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))
        graph_b = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))
        self.assertRaises(
            ValueError,
            fornax.api.Query.create,
            graph_a,
            graph_b,
            [(1, 'a', 1), (1, 2, 1), (2, 2, 1)]
        )

    def test_match_weight_raises(self):

        graph_a = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))
        graph_b = fornax.api.Graph.create(range(5), zip(range(2), range(2,5)))

        self.assertRaises(
            ValueError,
            fornax.api.Query.create,
            graph_a,
            graph_b,
            [(1, 1, 1.1), (1, 2, 1), (2, 2, 1)]
        )

        self.assertRaises(
            ValueError,
            fornax.api.Query.create,
            graph_a,
            graph_b,
            [(1, 1, 0), (1, 2, 1), (2, 2, 1)]
        ) 

        self.assertRaises(
            ValueError,
            fornax.api.Query.create,
            graph_a,
            graph_b,
            [(1, 1, 'b'), (1, 2, 1), (2, 2, 1)]
        )


class TestExecute(TestCaseDB):

    @classmethod
    def setUp(self):
        # trick fornax into using the test database setup
        super().setUp(self)
        fornax.api.Session = lambda: Session(self._connection)

        self.src = fornax.api.Graph.create(
            range(1, 6), 
            [(1, 3), (1, 2), (2, 4), (4, 5)]
        )

        self.target = fornax.api.Graph.create(
            range(1, 14),
            [
                (1, 2), (1, 3), (1, 4),
                (3, 7), (4, 5), (4, 6),
                (5, 7), (6, 8), (7, 10),
                (8, 9), (8, 12), (9, 10),
                (10, 11), (11, 12), (11, 13),
            ]
        )

        self.matches = [
            (1, 1, 1), (1, 4, 1), (1, 8, 1),
            (2, 2, 1), (2, 5, 1), (2, 9, 1),
            (3, 3, 1), (3, 6, 1), (3, 12, 1), (3, 13, 1),
            (4, 7, 1), (4, 10, 1),
            (5, 11, 1)
        ]

        self.query = fornax.api.Query.create(self.src, self.target, self.matches)
        self.payload = self.query.execute(n=2, edges=True)
        self.results = self.payload['subgraph_matches']
        self.subgraphs = [result['subgraph_match'] for result in self.results]

    def test_lim(self):
        self.assertEqual(len(self.subgraphs), 2)

    def test_scores(self):
            self.assertListEqual(
                [result['total_score'] for result in self.results],
                [0 for _ in self.results]
            )

    def test_subgraph_matches(self):
        self.assertIn([(1, 8), (2, 9), (3, 6), (4, 10), (5, 11)], self.subgraphs)
        self.assertIn([(1, 8), (2, 9), (3, 12), (4, 10), (5, 11)], self.subgraphs)

    def test_query_nodes(self):
        self.assertListEqual(self.payload['query_nodes'], [1, 2, 3, 4, 5])
    
    def test_query_edges(self):
        self.assertListEqual(self.payload['query_edges'], [(1, 2), (1, 3), (2, 4), (4, 5)])
    
    def test_target_nodes(self):
        self.assertListEqual(self.payload['target_nodes'], [6, 8, 9, 10, 11, 12])

    def test_target_edges(self):
        self.assertListEqual(
            self.payload['target_edges'],
            [(6, 8), (8, 9), (8, 12), (9, 10), (10, 11)]
        )