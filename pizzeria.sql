CREATE TABLE Pizze(
	ID SERIAL PRIMARY KEY,
	Nome TEXT NOT NULL,
	Prezzo MONEY
);

INSERT INTO Pizze (nome, prezzo)
VALUES
	('Margherita', 5.00),
	('Diavola', 6.50),
	('Capricciosa', 7.00);

CREATE TABLE Ingrediente(
	ID SERIAL PRIMARY KEY,
	Nome TEXT NOT NULL UNIQUE
);

INSERT INTO Ingrediente (nome)
VALUES
	('Pomodoro'),
	('Mozzarella'),
	('Salsiccia'),
	('Salame piccante');


CREATE TABLE IngredientePizza(
	ID SERIAL PRIMARY KEY,
	ID_Pizza INT REFERENCES Pizze(ID)
	ID_Ingrediente INT REFERENCES Ingrediente(ID)
);


SELECT * FROM Pizze;
SELECT * FROM Ingrediente;

INSERT INTO IngredientePizza (ID_Pizza, ID_Ingrediente)
VALUES
	(1, 1),
	(1, 2),
	(2, 1),
	(2, 2),
	(2, 3),
	(3, 1),
	(3, 2),
	(3, 4);


SELECT * FROM Pizze WHERE ID = 2;
SELECT COUNT(*) FROM Pizze;
SELECT SUM(Prezzo) FROM Pizze;
SELECT Nome FROM Ingrediente ORDER BY Nome DESC;

SELECT 
    p.nome AS Pizza,
    i.nome AS Ingrediente
FROM 
    Pizze p
JOIN 
    IngredientePizza ip ON p.id = ip.id_pizza
JOIN 
    Ingrediente i ON ip.id_ingrediente = i.id
ORDER BY 
    p.nome, i.nome;

SELECT 
    pizze.nome AS Pizza,
    ingrediente.nome AS Ingrediente
FROM 
    Pizze
JOIN IngredientePizza ON Pizze.ID = IngredientePizza.id_pizza
JOIN Ingrediente ON IngredientePizza.id_ingrediente = Ingrediente.ID

SELECT pizze.nome, ingrediente.nome
FROM Pizze, IngredientePizza, Ingrediente
WHERE IngredientePizza.id_Pizza = Pizze.id
AND IngredientePizza.id_ingrediente = Ingrediente.id;

ALTER TABLE IngredientePizza
ALTER COLUMN ID_Pizza SET NOT NULL,
ALTER COLUMN ID_Ingrediente SET NOT NULL;