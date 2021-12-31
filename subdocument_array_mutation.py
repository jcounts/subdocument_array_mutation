
def find_mutation(doc: dict, mutation: dict, description: str):
    """
    Recursivly searches through doc to find what needs to be changed, returning a description of the field.index that
    was modified
    The first call will only have a single field name as "description",
    subsequent calls will be of the form: field.index.field.index...etc

    example "mutation"s:
        {"_id": 2, "value": "too"}
        {"_id": 3, "mentions": [ {"_id": 5, "text": "pear"}]}
    """
    field = description.split('.')[-1]
    if not isinstance(doc[field], list):
        return {'$update': {description: mutation}}
    else:
        try:
            id_ = mutation.pop('_id')
        except KeyError:
            return {'$add': {description: [mutation]}}
        for index, item in enumerate(doc[field]):
            if doc[field][index]['_id'] == id_:
                mutated_key = list(mutation.keys())[0]
                if mutated_key == '_delete':
                    return {'$remove': {f"{description}.{index}": True}}
                if not isinstance(mutation[mutated_key], list):
                    new_mutation = mutation[mutated_key]
                else:
                    new_mutation = mutation[mutated_key][0]
                return find_mutation(doc[field][index], new_mutation, f"{description}.{index}.{mutated_key}")


def generate_update_statement(document: dict, mutation: dict) -> dict:
    """
    Returns a statement on what would be updated in the given document, based on the given mutation
    """
    key = list(mutation.keys())[0]
    updates = [find_mutation(document, item, key) for item in mutation[key]]
    results = {}
    for update in updates:
        operation = list(update.keys())[0]
        results[operation] = update[operation]
    return results
