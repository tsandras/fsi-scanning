import csv

from api import app, db, Product

def update_products_from_csv(csv_file_path):
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        total_products = 0
        for row in csv_reader:
            product_name = row['name']
            product = Product.query.filter_by(name=product_name).first()
            if product:
                print(f"Produit trouvé: {product_name} with id {product.id}")
                product.barcode = row['barcode']
                total_products += 1
                # db.session.commit()
        print(f"Total des produits mis à jour: {total_products}")

if __name__ == "__main__":
    csv_file_path = 'import.csv'
    with app.app_context():
        update_products_from_csv(csv_file_path)
    print("Mise à jour des produits terminée.")