import unittest.main
from unittest import TestCase, mock

from subdocument_array_mutation import find_mutation, generate_update_statement

TEST_DOC = {
    '_id': 1,
    'name': 'Johnny Content Creator',
    'posts': [
        {
            '_id': 2,
            'value': 'one',
            'mentions': []
        },
        {
            '_id': 3,
            'value': 'two',
            'mentions': [
                {
                    '_id': 5,
                    'text': 'apple'
                },
                {
                    '_id': 6,
                    'text': 'orange'
                }
            ]
        },
        {
            '_id': 4,
            'value': 'three',
            'mentions': []
        }
    ],
    'statuses': [
        {
            '_id': 1,
            'value': 'foo',
            'comments': []
        },
        {
            '_id': 2,
            'value': 'bar',
            'comments':
                [
                    {
                        '_id': 21,
                        'value': 'hello',
                        'replies':
                            [
                                {
                                    '_id': 1,
                                    'text': 'this is dog'
                                },
                                {
                                    '_id': 2,
                                    'text': 'how are you?'
                                }
                            ]
                    }
                ]
        },
    ]
}


class SubdocumentArrayMutationTests(TestCase):
    def test_find_mutation_update_case1(self):
        expected_output = {'$update': {'posts.0.value': 'too'}}
        actual_output = find_mutation(TEST_DOC, {'_id': 2, 'value': 'too'}, 'posts')
        self.assertEqual(actual_output, expected_output)

    def test_find_mutation_update_case2(self):
        expected_output = {'$update': {'posts.1.mentions.0.text': 'pear'}}
        actual_output = find_mutation(TEST_DOC, {'_id': 3, 'mentions': [{'_id': 5, 'text': 'pear'}]}, 'posts')
        self.assertEqual(actual_output, expected_output)

    def test_find_mutation_update_case3(self):
        expected_output = {'$update': {'statuses.1.comments.0.replies.1.text': 'this is cat'}}
        actual_output = find_mutation(
            TEST_DOC,
            {'_id': 2, 'comments': [{'_id': 21, 'replies': [{'_id': 2, 'text': 'this is cat'}]}]},
            'statuses'
        )
        self.assertEqual(actual_output, expected_output)

    def test_find_mutation_add_case1(self):
        expected_output = {'$add': {'posts': [{'value': 'four'}]}}
        actual_output = find_mutation(TEST_DOC, {'value': 'four'}, 'posts')
        self.assertEqual(actual_output, expected_output)

    def test_find_mutation_add_case2(self):
        expected_output = {'$add': {'posts.1.mentions': [{'text': 'banana'}]}}
        actual_output = find_mutation(TEST_DOC, {'_id': 3, 'mentions': [{'text': 'banana'}]}, 'posts')
        self.assertEqual(actual_output, expected_output)

    def test_find_mutation_add_case3(self):
        expected_output = {'$add': {'statuses.1.comments.0.replies': [{'text': 'this is cat'}]}}
        actual_output = find_mutation(
            TEST_DOC,
            {'_id': 2, 'comments': [{'_id': 21, 'replies': [{'text': 'this is cat'}]}]},
            'statuses'
        )
        self.assertEqual(actual_output, expected_output)

    def test_find_mutation_delete_case1(self):
        expected_output = {'$remove': {'posts.0': True}}
        actual_output = find_mutation(TEST_DOC, {'_id': 2, '_delete': True}, 'posts')
        self.assertEqual(actual_output, expected_output)

    def test_find_mutation_delete_case2(self):
        expected_output = {'$remove': {'posts.1.mentions.1': True}}
        actual_output = find_mutation(TEST_DOC, {"_id": 3, "mentions": [{"_id": 6, "_delete": True}]}, 'posts')
        self.assertEqual(actual_output, expected_output)

    def test_find_mutation_delete_case3(self):
        expected_output = {'$remove': {'statuses.1.comments.0.replies.1': True}}
        actual_output = find_mutation(
            TEST_DOC,
            {'_id': 2, 'comments': [{'_id': 21, 'replies': [{'_id': 2, '_delete': True}]}]},
            'statuses'
        )
        self.assertEqual(actual_output, expected_output)

    @mock.patch('subdocument_array_mutation.find_mutation')
    def test_generate_update_statement_single(self, mock_find_mutation):
        mock_find_mutation.return_value = {'$update': {'posts.0.value': 'too'}}
        result = generate_update_statement(TEST_DOC, {'posts': [{'_id': 2, 'value': 'too'}]})
        mock_find_mutation.assert_called_once_with(TEST_DOC, {'_id': 2, 'value': 'too'}, 'posts')
        self.assertEqual(result, mock_find_mutation.return_value)

    @mock.patch('subdocument_array_mutation.find_mutation')
    def test_generate_update_statement_multiple(self, mock_find_mutation):
        mock_find_mutation.side_effect = [
            {'$update': {'posts.0.value': 'too'}},
            {'$add': {'posts': [{'value': 'four'}]}},
            {'$remove': {'posts.0': True}}
        ]
        result = generate_update_statement(
            TEST_DOC,
            {'posts': [
                {'_id': 2, 'value': 'too'},
                {'value': 'four'},
                {'_id': 2, '_delete': True}
            ]}
        )
        mock_find_mutation.assert_has_calls([
            mock.call(TEST_DOC, {'_id': 2, 'value': 'too'}, 'posts'),
            mock.call(TEST_DOC, {'value': 'four'}, 'posts'),
            mock.call(TEST_DOC, {'_id': 2, '_delete': True}, 'posts')
        ])
        expected_result = {
            '$update': {'posts.0.value': 'too'},
            '$add': {'posts': [{'value': 'four'}]},
            '$remove': {'posts.0': True}
        }
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
