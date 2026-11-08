import { useState, type FormEvent } from "react";

import { useCreateExample, useExamples } from "./api";

export function ExamplesPage() {
  const examples = useExamples();
  const createExample = useCreateExample();
  const [name, setName] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    createExample.mutate({ name }, { onSuccess: () => setName("") });
  }

  return (
    <section>
      <h1>Exemplos</h1>

      <form onSubmit={handleSubmit}>
        <label htmlFor="example-name">Nome</label>
        <input
          id="example-name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          maxLength={100}
          required
        />
        <button type="submit" disabled={createExample.isPending}>
          Adicionar
        </button>
      </form>
      {createExample.isError && (
        <p role="alert">Não foi possível salvar o exemplo.</p>
      )}

      {examples.isPending && <p>Carregando...</p>}
      {examples.isError && (
        <p role="alert">Não foi possível carregar os exemplos.</p>
      )}
      {examples.data?.length === 0 && <p>Nenhum exemplo cadastrado.</p>}
      <ul>
        {examples.data?.map((example) => (
          <li key={example.id}>{example.name}</li>
        ))}
      </ul>
    </section>
  );
}
