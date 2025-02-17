fn calculadora(op: char, x: float, y: float) -> float {
    if op == '+' {
        return x + y;
    }
    else if op == '-'{
        return x - y;
    }
    else if op == '*'{
        return x * y;
    }
    else if op == '/' {
        if y == 0.0 {
            return 0.0;
        }
        return x / y;
    }
    return 0.0;
}

fn main(){ 
    let a, b: float;
    a = 1.8;
    b = 7.2;
    println("{}", calculadora('*', a, b));
}
