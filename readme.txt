this is a small compiler I wrote
all code goes in functions, all assignments are to variables.
all variables are signed 64 bit numbers (long long, or i64)
the compiler outputs masm x64 asm code
here is a sample implemantation of quick sort:

//all variables are 8 bytes, so (a + 8 * b) would be the memory slot where a[b] would start
fn ind a, b: return a + 8 * b;

//returns 1 if arr[a] < arr[b] else 0
fn cmp_lt arr, a, b: {
    let a_val = *ind(arr, a);
    let b_val = *ind(arr, b);
    return a_val < b_val;
}

//swaps inplace arr[a] and arr[b]
fn swap arr, a, b: {
    let tmp_a = *ind(arr, a);
    let tmp_ind = ind(arr, a);
    tmp_ind := *ind(arr, b);
    tmp_ind = ind(arr, b);
    tmp_ind := tmp_a;
    return 0;
}

//places the last element of the array in it's sorted index
//all smaller element to the left of it and the larger elements to the right of it
fn partition arr, len: {
    let pivot = *ind(arr, len - 1);
    let i = 0;
    let small_ind = 0;
    while i < len - 1 {
        if cmp_lt(arr, i, len - 1) {
            swap(arr, i, small_ind);
            small_ind = small_ind + 1;
        }
        i = i + 1;
    }
    swap(arr, len - 1, small_ind);
    return small_ind;
}

//gets a sequantal memory slice and a length
//sorts the slice
fn quick_sort arr, len: {
    if len < 2 {
        return 0;
    }
    let split = partition(arr, len);
    quick_sort(arr, split);
    quick_sort(ind(arr, split + 1), len - split - 1);
    return 0;
}