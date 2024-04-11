import multiprocessing as mp
from collections import defaultdict

class DictionaryMerger:
    @staticmethod
    def merge_dicts(dicts_list):
        # Function to merge dictionaries
        def merge_dicts_worker(input_dict, output_pipe):
            merged_dict = defaultdict(list)
            for d in input_dict:
                for key, value in d.items():
                    merged_dict[key].extend(value)
            output_pipe.send(merged_dict)
            output_pipe.close()

        # Split the input list of dictionaries into chunks for parallel processing
        process_count = mp.cpu_count()
        splits = DictionaryMerger.split(dicts_list, process_count // 2)
        print(splits)

        # Create pipes for communication between processes
        tasks = []
        pipe_list = []
        for split in splits:
            print(split)
            recv_end, send_end = mp.Pipe(False)
            j = mp.Process(target=merge_dicts_worker, args=(split, send_end))
            tasks.append(j)
            pipe_list.append(recv_end)
            j.start()

        # Collect merged dictionaries from processes
        merged_dict = defaultdict(list)
        for (i, task) in enumerate(tasks):
            d = pipe_list[i].recv()
            print(d)
            for key, value in d.items():
                merged_dict[key].extend(value)
            task.join()
            
        return merged_dict
    
    @staticmethod
    def split(a, n):
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

# Example usage
if __name__ == "__main__":
    dicts = [{"a": [1, 2]}, {"b": [3, 4]}, {"a": [5, 6]}, {"a": [1, 2]}, {"b": [3, 4]}, {"a": [5, 6]}, {"a": [1, 2]}, {"b": [3, 4]}, {"a": [5, 6]}]
    merged_dict = DictionaryMerger.merge_dicts(dicts)
    print(merged_dict)