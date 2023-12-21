this is a small compiler I wrote
all code goes in functions, all assignments are to variables.
all variables are signed 64 bit numbers (long long, or i64)
the compiler outputs masm x64 asm code
here is a sample implemantation of quick sort:
fn ind a, b: return a + 8 * b;
fn cmp_lt arr, a, b: {
    let a_val = *ind(arr, a);
    let b_val = *ind(arr, b);
    return a_val < b_val;
}
fn cmp_le arr, a, b: {
    let a_val = *ind(arr, a);
    let b_val = *ind(arr, b);
    return a_val <= b_val;
}
fn read arr, index: {
    return *ind(arr, index);
}
fn write arr, index, value: {
    let mem_slot = ind(arr, index);
    mem_slot := value;
    return 0;
}
fn swap arr, a, b: {
    let tmp_a = *ind(arr, a);
    let tmp_ind = ind(arr, a);
    tmp_ind := *ind(arr, b);
    tmp_ind = ind(arr, b);
    tmp_ind := tmp_a;
    return 0;
}
fn partition arr, len: {
    let pivot = read(arr, len - 1);
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
fn quick_sort arr, len: {
    if len < 2 {
        return 0;
    }
    let split = partition(arr, len);
    quick_sort(arr, split);
    quick_sort(ind(arr, split + 1), len - split - 1);
    return 0;
}