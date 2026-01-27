# Assembly and SIMD

## Safe `#[target_feature]`

Safe functions can use `#[target_feature]`. Callable from other target-feature functions or with runtime checks.

```rust
#[target_feature(enable = "avx2")]
fn simd_operation(data: &[f32]) -> f32 {
    data.iter().sum()
}

fn main() {
    if is_x86_feature_detected!("avx2") {
        unsafe { simd_operation(&data) }
    }
}
```

## Inline Assembly Labels

`asm!` supports jumping to Rust code blocks via labels.

```rust
use std::arch::asm;

let mut x = 0;
unsafe {
    asm!(
        "test {val}, {val}",
        "jz {zero}",
        "mov {val}, 42",
        "jmp {done}",
        val = inout(reg) x,
        zero = label { x = 0; },
        done = label {},
    );
}
```

Label blocks must return `()` or `!` (never type).

## `cfg` Attributes on `asm!` Lines

Conditionally compile individual assembly statements.

```rust
use std::arch::asm;

unsafe {
    asm!(
        "nop",
        #[cfg(target_feature = "sse2")]
        "movaps xmm0, xmm1",
        #[cfg(target_feature = "avx")]
        "vmovaps ymm0, ymm1",
        "nop",
    );
}
```

Works with operands too:

```rust
asm!(
    "mov eax, {val}",
    #[cfg(feature = "extended")]
    val = const 42,
    #[cfg(not(feature = "extended"))]
    val = const 0,
);
```

Works with `asm!`, `global_asm!`, and `naked_asm!`.

## Naked Functions

Full control over assembly generation with `#[unsafe(naked)]`. No compiler-generated prologue/epilogue.

```rust
use core::arch::naked_asm;

#[unsafe(naked)]
pub unsafe extern "sysv64" fn add_one(x: u64) -> u64 {
    naked_asm!(
        "lea rax, [rdi + 1]",
        "ret"
    );
}
```

Must contain exactly one `naked_asm!` call. Useful for:
- OS kernels and bootloaders
- Interrupt handlers
- Custom calling conventions
- compiler-builtins implementations
