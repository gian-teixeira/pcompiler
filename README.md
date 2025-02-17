# pcompiler

> Giancarlo Oliveira Teixeira

Compilador da **linguagem P**.

> A linguagem p é uma linguagem de programação didática criada pelo profesor
Alexandre Bittencourt Pigozzo. O trabalho desenvolvido na matéria de compiladores
da Universidade Federal de São João del-Rei no período 2024/2.

## Execução

```
./pcompiler <source_file>
```

### Resultado parcial

Nesta versão, estão implementados apenas os analisadores léxico, sintático e
algumas partes da análise semântica (verificação de tipos e verificação de
declaração de variáveis). A execução gera alguns arquivos, que são colocados
na pasta `log`:

- `log.txt` : mensagens gerais geradas durante a execução
- `semantic_errors.txt`: os erros semânticos encontrados
- `syntatic_errors.txt`: os errors sintáticos encontrados
- `function_*_ST.txt`: entradas da tabela de símbolos da função *
- `function_*_AST.txt`: representação em JSON da árvore de sintaxe abstrata da função *

Alguns arquivos de teste, com entradas e saídas, estão disponíveis na
pasta *test*.
