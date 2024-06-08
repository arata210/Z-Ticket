-- ������ݿ�
drop database cinema;

-- ����cinema���ݿ�
CREATE DATABASE cinema
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

-- ʹ�����ݿ�
use cinema;

-- ������Ӱ�� film
CREATE TABLE film (
    movie_id CHAR(10) PRIMARY KEY, -- ��Ӱid
    title VARCHAR(255), -- ����
    release_date CHAR(10), -- ��ӳʱ��
    country VARCHAR(255), -- ����/����
    length INT, -- ʱ��
    director VARCHAR(255), -- ����
    genre VARCHAR(100), -- ����
    actor VARCHAR(255), -- ��Ҫ��Ա
    rating_num CHAR(10) -- ����
);

-- ��ʼ����Ӱ��
INSERT INTO film (movie_id, title, release_date, country, length, director, genre, actor, rating_num)
VALUES 
('35725869', '��᲻��ͣ��', '2023-12-29', '�й���½', 117, '������', '���� / ϲ��', '���� / �׿� / ׯ��� / ��Ѹ', '8.2'),
('35074609', '����ָ', '2023-12-30', '�й���� / �й���½', 125, 'ׯ��ǿ', '���� / ����', '����ΰ / ���»� / ��׿�� / �δﻪ', '6.4'),
('35927496', 'Ǳ��', '2023-12-29', '�й���½ / �й����', 114, '����ҫ', '���� / ���� / ����', '���»� / �ּҶ� / ������ / ����ɪ', '5.9'),
('35768712', 'һ��һ��������', '2023-12-30', '�й���½', 107, '��С�� / ����', '���� / ���', '������ / �ż��� / ��ݼ / ������', '6.1'),
('35312439', '������', '2024-01-11', '�й���½', 109, '�¹��� / ������', '����', '���� / ��� / �պ� / ������ķ', '��������');

-- ���������� ticket_order
CREATE TABLE ticket_order (
    order_id CHAR(20) NOT NULL, -- ����id
    phone CHAR(11), -- �ֻ���
    session_id CHAR(20), -- ����id
    actual_price DECIMAL(6,2), -- ʵ��֧�����
    count INT, -- ����
    seat CHAR(20), -- ��λ
    datetime DATETIME, -- ֧��ʱ��
    payment CHAR(20), -- ֧����ʽ
    code CHAR(10), -- ȡƱ��
    PRIMARY KEY (order_id)
);

-- �����û��� user
CREATE TABLE user (
    -- uid CHAR(10) NOT NULL, �û�id
    phone CHAR(11) NOT NULL, -- �ֻ���
    pid CHAR(15), -- ����id
    -- name VARCHAR(20), �û���
    -- type CHAR(6), �û�����
    balance DECIMAL(6,2), -- �û����
    -- status BOOL, -- �û�״̬
    PRIMARY KEY (phone)
);

-- ���������� parameter
CREATE TABLE parameter (
    pid CHAR(15) NOT NULL, -- ����id
    pname CHAR(20), -- ������
    pvalue FLOAT(10), -- �ۿ���
    PRIMARY KEY (pid)
);

-- ��������¼�� pay_amount
CREATE TABLE pay_amount (
    original_price DECIMAL(6,2), -- ԭʼ�۸�
    coupon_amount DECIMAL(6,2), -- �Ż�ȯ�۸�
    parameter_amount DECIMAL(6,2), -- Ӱ�ǿ��۸�
    actual_price DECIMAL(6,2), -- ʵ��֧�����
    order_id CHAR(20), -- ����id
    PRIMARY KEY (order_id)
);

-- �������Լ��
ALTER TABLE pay_amount ADD CONSTRAINT FK_order FOREIGN KEY (order_id)
      REFERENCES ticket_order (order_id);

ALTER TABLE ticket_order ADD CONSTRAINT FK_have FOREIGN KEY (phone)
      REFERENCES user (phone);

ALTER TABLE user ADD CONSTRAINT FK_benefit FOREIGN KEY (pid)
      REFERENCES parameter(pid);

-- ��ʼ�������� parameter
INSERT INTO parameter (pid, pname, pvalue)
VALUES
  ('P000', '��ͨ��', 1),
  ('P001', '�·ѿ�', -5),
  ('P002', '��ֵ��', 0.8);

-- ��ʼ���û��� user
INSERT INTO user (phone, pid, balance)
VALUES
    ('13812345678', 'P000', 0),
    ('13987654321', 'P001', 0),
    ('18788886666', 'P002', 176);

-- ��ʼ�������� ticket_order
INSERT INTO ticket_order (order_id, phone, actual_price, session_id, count, seat, datetime, payment, code)
VALUES
('S0123', '13812345678', 29.00, '35725869001', 1, 'Z��1��', '2024-01-05 19:45:00', '֧����', '123456'),
('S0124', '13987654321', 25.00, '35725869001', 1, 'Z��2��', '2024-01-06 15:30:00', '΢��', '223344'),
('S0125', '18788886666', 24.00, '35725869001', 1, 'Z��3��', '2024-01-07 16:00:00', '��ֵ��', '778855');

-- ��ʼ������¼�� pay_amount
INSERT INTO pay_amount (original_price, coupon_amount, parameter_amount, actual_price, order_id)
VALUES
   (30.00, 1.00, 0.00, 29.00, 'S0123'),
   (30.00, 0.00, 5.00, 25.00, 'S0124'),
   (30.00, 0.00, 6.00, 24.00, 'S0125');

-- ��ѯ�û���
SELECT * FROM user;

-- ��ѯ��Ӱ��
SELECT * FROM film;

-- ��ѯ�����ͽ���¼��Ĳ���
SELECT
    a.order_id AS ������,
    a.session_id AS ����ID,
    a.count AS ��������,
    a.seat AS ��λ��,
    a.phone AS �ֻ���,
    a.actual_price AS ʵ��֧��,
    a.datetime AS ����ʱ��,
    a.payment AS ֧����ʽ,
    a.code AS ȡƱ��,
    b.original_price AS ԭ��,
    b.coupon_amount AS �Ż�ȯ,
    b.parameter_amount AS Ӱ�ǿ�
FROM ticket_order AS a
JOIN pay_amount AS b ON a.order_id = b.order_id;
